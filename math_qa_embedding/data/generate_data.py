import json
import random
import os

# Tạo dữ liệu mẫu về toán lớp 1
def generate_math_qa():
    # Các dạng bài cộng, trừ đơn giản
    addition_questions = []
    subtraction_questions = []
    comparison_questions = []
    word_problems = []
    
    # Tạo câu hỏi cộng
    for i in range(50):
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        question = f"Tính {a} + {b} = ?"
        answer = f"{a} + {b} = {a + b}"
        addition_questions.append({"question": question, "answer": answer})
    
    # Tạo câu hỏi trừ
    for i in range(50):
        a = random.randint(10, 30)
        b = random.randint(1, a)
        question = f"Tính {a} - {b} = ?"
        answer = f"{a} - {b} = {a - b}"
        subtraction_questions.append({"question": question, "answer": answer})
    
    # Tạo câu hỏi so sánh
    for i in range(30):
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        question = f"So sánh {a} và {b} bằng dấu >, <, ="
        if a > b:
            answer = f"{a} > {b}"
        elif a < b:
            answer = f"{a} < {b}"
        else:
            answer = f"{a} = {b}"
        comparison_questions.append({"question": question, "answer": answer})
    
    # Tạo các bài toán có lời văn
    word_problem_templates = [
        {
            "template": "Hải có {} quả táo. Hải được mẹ cho thêm {} quả táo. Hỏi Hải có tất cả bao nhiêu quả táo?",
            "operation": "addition"
        },
        {
            "template": "Lan có {} cái kẹo. Lan ăn mất {} cái kẹo. Hỏi Lan còn lại bao nhiêu cái kẹo?",
            "operation": "subtraction"
        },
        {
            "template": "Bình có {} quyển sách. Nam có {} quyển sách. Hỏi hai bạn có tất cả bao nhiêu quyển sách?",
            "operation": "addition"
        },
        {
            "template": "Trên cây có {} con chim. Có {} con chim bay đi. Hỏi trên cây còn lại bao nhiêu con chim?",
            "operation": "subtraction"
        },
        {
            "template": "Bố mua {} quả cam và {} quả quýt. Hỏi bố mua tất cả bao nhiêu quả?",
            "operation": "addition"
        }
    ]
    
    for i in range(50):
        template = random.choice(word_problem_templates)
        if template["operation"] == "addition":
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            question = template["template"].format(a, b)
            answer = f"{a} + {b} = {a + b}"
        else:  # subtraction
            a = random.randint(5, 20)
            b = random.randint(1, a)
            question = template["template"].format(a, b)
            answer = f"{a} - {b} = {a - b}"
        word_problems.append({"question": question, "answer": answer})
    
    # Gộp tất cả các loại câu hỏi
    all_questions = addition_questions + subtraction_questions + comparison_questions + word_problems
    random.shuffle(all_questions)
    
    return all_questions

def save_data():
    data = generate_math_qa()
    # Tạo data directory nếu chưa tồn tại
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_qa_data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Đã tạo {len(data)} câu hỏi và lưu vào file math_qa_data.json")

if __name__ == "__main__":
    save_data() 