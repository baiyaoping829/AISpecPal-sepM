import pdfkit
import os

# 读取HTML文件内容
with open('test_report.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 尝试生成PDF
try:
    # 直接使用pdfkit转换
    pdfkit.from_string(html_content, 'test_report.pdf')
    print("PDF报告生成成功: test_report.pdf")
except Exception as e:
    print(f"PDF生成失败: {e}")
    print("请确保已安装wkhtmltopdf并添加到系统PATH")
    # 作为备选方案，复制HTML文件
    print("已创建HTML格式的测试报告: test_report.html")