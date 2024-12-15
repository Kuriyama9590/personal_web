from openai import OpenAI

client = OpenAI(api_key="sk-34501009c15d4f008000608f30158142", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "根据给出日程行为描述，在“工作”，“学习”，“摸鱼”，“整活”四种行为中进行判断，找出最契合的一种，直接输出具体日程为：阅读老师给的代码，完成python脚本"},
    ],
    stream=False
)

print(response.choices[0].message.content)