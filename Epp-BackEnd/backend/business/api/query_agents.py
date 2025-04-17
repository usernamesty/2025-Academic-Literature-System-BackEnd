from django.http import JsonResponse, HttpRequest
from baidusearch.baidusearch import search
import json
from business.utils.agent_chats import create_chat_func,NoAPIKeyError
from business.utils.reply import fail, success
from business.utils.agent_functions import method_dict
from django.views.decorators.http import require_http_methods

generual_system_prompt = "You are a helpful assistant."
import traceback

@require_http_methods(['POST'])
def query_llm(request):
    data = json.loads(request.body)
    llm = data.get('llm') #选择的语言模型名称，比如deepseek-r1, deepseek-v3
    max_tokens = data.get('max_tokens') if data.get('max_tokens') else 2048
    query_content = data.get('query_content') #用户输入的查询语句
    historys = data.get('historys')
    chat_func = create_chat_func(llm) if llm else create_chat_func("deepseek-v3")
    system_prompt = generual_system_prompt
    if historys:
        historys = json.loads(historys)
        historys.append({"role": "user", "content": query_content})
        messages = historys
        print(messages)
    else:
        messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query_content}
                ]
    try:
        response = chat_func(messages=messages, max_tokens=max_tokens)
        if(isinstance(response,str)):
            assistant_content = response
        else:
            assistant_content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_content})
        return success(data={"assistant_content": assistant_content,"historys": json.dumps(messages, ensure_ascii=False, indent=4)}, msg="询问成功")
    except NoAPIKeyError:
        return fail(msg=str("请检查系统环境变量是否有相应的api_key"))
    except Exception as e:
        print(response)
        traceback.print_exc()
        return fail(msg=str("调用llm发生错误,请检查后端报错信息"))
    

@require_http_methods(['POST'])
def query_deepseek_v3_with_function(request):
    data = json.loads(request.body)
    tools = []
    function_names = data.get('function_names',[]) #要调用的方法名列表
    for function_name in function_names:
        if function_name in method_dict:
            tools.append({"type":"function", "function": method_dict[function_name].description})
        else:
            return fail(msg=str("方法名不存在"))
    # tools = [{"type":"function", "function": method.description} for method in method_dict.values()]
    query_content = data.get('query_content') #用户输入的查询语句
    deepseek_v3_chat_func = create_chat_func("deepseek-v3")
    historys = data.get('historys')
    if historys:
        historys = json.loads(historys)
        historys.append({"role": "user", "content": query_content})
        messages = historys
    else:
        messages = [
                    {"role": "user", "content": query_content}
                ]
    print(messages)
    try:
        response = deepseek_v3_chat_func(messages=messages, max_tokens=4096,tools=tools)
        assistant_message = response.choices[0].message
        print(assistant_message.model_dump_json())
        # print(json.dumps(assistant_message, ensure_ascii=False, indent=4))
        if assistant_message.tool_calls: # 有工具调用
            tool = assistant_message.tool_calls[0]
            messages.append(assistant_message)
            function_name = tool.function.name
            argumets = json.loads(tool.function.arguments)
            try:
                function = method_dict[function_name].method
                result = function(argumets)
                messages.append({"role": "tool", "tool_call_id": tool.id, "content": result})
                assistant_content_to_user = deepseek_v3_chat_func(messages=messages, max_tokens=4096,tools=tools).choices[0].message.content
                messages.append({"role": "assistant", "content": assistant_content_to_user})
            except Exception as e:
                traceback.print_exc()
                return fail(msg=str("方法调用失败"))
        else: # 无工具调用
            assistant_content_to_user = assistant_message.content
            assert assistant_content_to_user, "assistant_content_to_user is None"
            messages.append({"role": "assistant", "content": assistant_content_to_user})
        store_messages = []
        for message in messages:
            if isinstance(message,dict):
                store_messages.append(message)
            else: #deepseek v3的function call调用格式无法json化，推测tools数据在它们的后端有后处理，这里只能自行处理
                tool = message.tool_calls[0]
                store_messages.append({"role": "assistant", "tool_calls": [{"id":tool.id,"type":"function","function":{"name":tool.function.name,"arguments":tool.function.arguments}}]})
        print(store_messages)
        return success(data={"assistant_content_to_user": assistant_content_to_user,"historys": json.dumps(store_messages, ensure_ascii=False, indent=4)}, msg="询问成功")
    except NoAPIKeyError:
        return fail(msg=str("请检查系统环境变量是否有相应的api_key"))
    except Exception as e:
        traceback.print_exc()
        return fail(msg=str("调用llm发生错误,请检查后端报错信息"))


@require_http_methods(["POST"])
def query_with_SE(request):
    # 获取信息
    data = json.loads(request.body)
    query_content = data.get('query_content')
    max_token = data.get('max_token')
    llm = data.get('llm')
    history = data.get('history')

    # 异常处理
    if not query_content:
        return JsonResponse({'error': 'Missing query_content parameter'}, status=400)
    # 搜索
    results = search(query_content)
    i=0
    top_five_results=[]
    for result in results:
        i = i+1
        top_five_results.append(result)
        if i==5:
            break
    results=top_five_results

    prompt = f"{query_content}，并结合以下信息回答问题{results}。答案中不需要列举这些信息"
    if history:
        history=json.loads(history)
        history.append({"role":"user","content":prompt})
        messages=history
    else:
        messages=[{"role":"user","content":prompt}]
    chat_func = create_chat_func(llm) if llm else create_chat_func("deepseek-v3")
    try:
        response = chat_func(messages=messages, max_tokens=max_token)
        if(isinstance(response,str)):
            assistant_content = response
        else:
            assistant_content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_content})
        return success(data={"assistant_content": assistant_content,"historys": json.dumps(messages, ensure_ascii=False, indent=4)}, msg="询问成功")
    except NoAPIKeyError:
        return fail(msg=str("请检查系统环境变量是否有相应的api_key"))
    except Exception as e:
        print(response)
        traceback.print_exc()
        return fail(msg=str("调用llm发生错误,请检查后端报错信息"))
