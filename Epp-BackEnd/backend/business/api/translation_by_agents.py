from django.http import JsonResponse, HttpRequest
import json
from business.utils.agent_chats import create_chat_func,NoAPIKeyError
from business.utils.reply import fail, success
from django.views.decorators.http import require_http_methods

translation_system_prompt_template = \
"""
你是一个翻译专家，将用户输入的{{Source_language}}翻译成{{target_language}}。
用户可以向助手发送需要翻译的内容，助手会回答相应的翻译结果，并确保符合{{target_language}}语言习惯，你可以调整语气和风格，并考虑到某些词语的文化内涵和地区差异。
要求：
1、作为翻译家，需将原文翻译成具有信达雅标准的译文。"信" 即忠实于原文的内容与意图；"达" 意味着译文应通顺易懂，表达清晰；"雅" 则追求译文的文化审美和语言的优美。
目标是创作出既忠于原作精神，又符合目标语言文化和读者审美的翻译。
2、只返回翻译后的译文,不要说其它话。
3、对于原文中出现的目标语言,请保持原样,只翻译不是目标语言的部分。
"""

translation_system_prompt_template_only_target_language = \
"""
你是一个{{target_language}}翻译专家，将用户输入的语言翻译成{{target_language}}。
用户可以向助手发送需要翻译的内容，助手会回答相应的翻译结果，并确保符合{{target_language}}语言习惯，你可以调整语气和风格，并考虑到某些词语的文化内涵和地区差异。
要求：
1、作为翻译家，需将原文翻译成具有信达雅标准的译文。"信" 即忠实于原文的内容与意图；"达" 意味着译文应通顺易懂，表达清晰；"雅" 则追求译文的文化审美和语言的优美。
目标是创作出既忠于原作精神，又符合目标语言文化和读者审美的翻译。
2、只返回翻译后的译文,不要说其它话。
3、对于原文中出现的目标语言,请保持原样,只翻译不是目标语言的部分。
"""

@require_http_methods(['POST'])
def translate_by_llm(request):
    data = json.loads(request.body)
    source_text = data.get('source_text')
    source_language = data.get('source_language')
    target_language = data.get('target_language')
    llm = data.get('llm') #选择的语言模型名称，比如deepseek-r1, deepseek-v3
    max_tokens = data.get('max_tokens') if data.get('max_tokens') else 2048
    chat_func = create_chat_func(llm) if llm else create_chat_func("deepseek-v3")
    if source_language:
        system_prompt = translation_system_prompt_template.format(Source_language=source_language, target_language=target_language) 
    else:
        system_prompt = translation_system_prompt_template_only_target_language.format(target_language=target_language)
    messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": source_text}
            ]
    try:
        response = chat_func(messages=messages, max_tokens=max_tokens,temperature=1.3)
        if(isinstance(response,str)):
            target_text = response
        else:
            target_text = response.choices[0].message.content
        return success(data={"target_text": target_text},msg="翻译成功")
    except NoAPIKeyError:
        return fail(msg=str("请检查系统环境变量是否有相应的api_key"))
    except Exception as e:
        print(response)
        print(e)
        return fail(msg=str("调用llm发生错误,请检查后端报错信息"))



