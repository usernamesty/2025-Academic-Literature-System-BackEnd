import io
import sys
import cmath
import json
from fpdf import FPDF
import os


# 定义一个类来存储方法和其介绍
class MethodInfo:
    def __init__(self, name, method, description):
        self.func_name = name
        self.method = method
        self.description = description


# 丰富后的读取文件功能，不仅统计行数，还统计单词数和字符数
def read_file_and_count_info(params):
    file_path = params.get('file_path')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            lines = content.splitlines()
            words = content.split()
            line_count = len(lines)
            word_count = len(words)
            char_count = len(content)
            result = {
                "line_count": line_count,
                "word_count": word_count,
                "char_count": char_count
            }
            return json.dumps(result, ensure_ascii=False)
    except FileNotFoundError:
        error_result = {"error": f"错误: 文件 {file_path} 未找到。"}
        return json.dumps(error_result, ensure_ascii=False)
    except Exception as e:
        error_result = {"error": f"发生未知错误: {e}"}
        return json.dumps(error_result, ensure_ascii=False)


# 新增的数学方法，求解一元二次方程 ax^2 + bx + c = 0
def solve_quadratic_equations(params):
    a = params.get('a')
    b = params.get('b')
    c = params.get('c')
    if a == 0:
        if b == 0:
            if c == 0:
                result = {"solution": "方程有无数解"}
            else:
                result = {"solution": "方程无解"}
        else:
            x = -c / b
            result = {"solution": f"方程为一元一次方程，解为 x = {x}"}
    else:
        discriminant = (b ** 2) - (4 * a * c)
        sol1 = (-b - cmath.sqrt(discriminant)) / (2 * a)
        sol2 = (-b + cmath.sqrt(discriminant)) / (2 * a)
        if discriminant >= 0:
            result = {"solution": f"方程有两个实数解: x1 = {sol1.real}, x2 = {sol2.real}"}
        else:
            result = {"solution": f"方程有两个复数解: x1 = {sol1}, x2 = {sol2}"}
    return json.dumps(result, ensure_ascii=False)


# 定义执行大模型写的 Python 代码的方法
def execute_python_code(params):
    code = params.get('code')
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    try:
        exec(code)
        output = new_stdout.getvalue()
        result = {"output": output}
    except Exception as e:
        result = {"error": f"执行代码时出错: {str(e)}"}
    finally:
        sys.stdout = old_stdout

    return json.dumps(result, ensure_ascii=False)


def save_content_to_file(params):
    content = params.get('content')
    file_name = params.get('file_name')
    file_format = params.get('file_format')
    target_path = params.get('target_path')
    if target_path is None:
        target_path = os.path.join(os.getcwd(), 'business', 'utils', 'AI_OUTPUT')
    if not os.path.exists(target_path):
        error_result = {"error": f"错误: 目标路径 {target_path} 不存在。"}
        return json.dumps(error_result, ensure_ascii=False)
    if file_format.lower() == 'md':
        try:
            file_path = os.path.join(target_path, f"{file_name}.md")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            result = {"message": f"成功保存为 {file_path}"}
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            error_result = {"error": f"保存为 Markdown 文件时出错: {e}"}
            return json.dumps(error_result, ensure_ascii=False)
    elif file_format.lower() == 'pdf':
        try:
            file_path = os.path.join(target_path, f"{file_name}.pdf")
            pdf = FPDF()
            pdf.add_page()
            # 这里需要更改为本地路径！
            pdf.add_font("Microsoft YaHei", "", "D:\\ruangong\\2025-Academic-Literature-System\\Epp-BackEnd\\backend\\msyh.ttf", uni=True)
            pdf.set_font("Microsoft YaHei", size=12)
            pdf.multi_cell(0, 10, txt=content)
            pdf.output(file_path)
            result = {"message": f"成功保存为 {file_path}"}
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            error_result = {"error": f"保存为 PDF 文件时出错: {e}"}
            return json.dumps(error_result, ensure_ascii=False)
    else:
        error_result = {"error": f"不支持的文件格式: {file_format}"}
        return json.dumps(error_result, ensure_ascii=False)


# 为 read_file_and_count_info 方法创建详细描述
read_file_description = {
    "name": "read_file_and_count_info",
    "description": "读取本地文件，统计文件的行数、单词数和字符数，并以字典形式返回统计结果。若文件不存在或出现其他错误，将返回错误信息。",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "要读取的文件的路径"
            }
        },
        "required": [
            "file_path"
        ]
    }
}

# 为 solve_quadratic_equations 方法创建详细描述
solve_quadratic_description = {
    "name": "solve_quadratic_equations",
    "description": "求解一元二次方程 ax^2 + bx + c = 0 的解。考虑了 a = 0 时的特殊情况，会根据判别式的值判断方程解的情况，返回实数解或复数解。",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {
                "type": "number",
                "description": "一元二次方程中 x^2 的系数"
            },
            "b": {
                "type": "number",
                "description": "一元二次方程中 x 的系数"
            },
            "c": {
                "type": "number",
                "description": "一元二次方程中的常数项"
            }
        },
        "required": [
            "a", "b", "c"
        ]
    }
}

# 为 execute_python_code 方法创建详细描述
execute_python_code_description = {
    "name": "execute_python_code",
    "description": "执行大模型生成的 Python 代码，并返回代码执行的输出结果。若代码执行出错，将返回错误信息。",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "要执行的 Python 代码"
            }
        },
        "required": [
            "code"
        ]
    }
}

# 为 save_content_to_file 方法创建详细描述
save_content_description = {
    "name": "save_content_to_file",
    "description": "将大模型生成的内容保存为指定格式的文件，目前支持 Markdown 和 PDF 格式。",
    "parameters": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "要保存的内容"
            },
            "file_name": {
                "type": "string",
                "description": "保存的文件名（不包含扩展名）"
            },
            "file_format": {
                "type": "string",
                "description": "目标文件格式，可选值为 'md' 或 'pdf'"
            },
            "target_path": {
                "type": "string",
                "description": "保存的文件的目标路径，默认为当前工作目录"
            }
        },
        "required": [
            "content", "file_name", "file_format"
        ]
    }
}

# 创建 MethodInfo 类的实例
read_file_info = MethodInfo(
    name="read_file_and_count_info",
    method=read_file_and_count_info,
    description=read_file_description
)

solve_quadratic_info = MethodInfo(
    name="solve_quadratic_equations",
    method=solve_quadratic_equations,
    description=solve_quadratic_description
)

execute_python_code_info = MethodInfo(
    name="execute_python_code",
    method=execute_python_code,
    description=execute_python_code_description
)

save_content_info = MethodInfo(
    name="save_content_to_file",
    method=save_content_to_file,
    description=save_content_description
)

# 创建字典，存储方法名到类的映射
method_dict = {
    read_file_info.func_name: read_file_info,
    solve_quadratic_info.func_name: solve_quadratic_info,
    execute_python_code_info.func_name: execute_python_code_info,
    save_content_info.func_name: save_content_info
}
    