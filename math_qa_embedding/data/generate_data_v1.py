import json
import random
import os

# Cấu trúc dữ liệu cho các chương và bài
chuong_bai_structure = {
    "Chương 1: Các số đến 10": [
        "Bài 1: Đếm đến 5",
        "Bài 2: Đếm đến 10",
        "Bài 3: So sánh các số trong phạm vi 10",
        "Bài 4: Thứ tự các số đến 10"
    ],
    "Chương 2: Phép cộng trong phạm vi 10": [
        "Bài 1: Phép cộng đến 5",
        "Bài 2: Phép cộng đến 10",
        "Bài 3: Bảng cộng trong phạm vi 10",
        "Bài 4: Tính nhẩm phép cộng"
    ],
    "Chương 3: Phép trừ trong phạm vi 10": [
        "Bài 1: Phép trừ đến 5",
        "Bài 2: Phép trừ đến 10",
        "Bài 3: Bảng trừ trong phạm vi 10",
        "Bài 4: Tính nhẩm phép trừ"
    ],
    "Chương 4: Các số đến 20": [
        "Bài 1: Đếm đến 20",
        "Bài 2: Số hàng chục, số hàng đơn vị",
        "Bài 3: So sánh các số trong phạm vi 20",
        "Bài 4: Thứ tự các số đến 20"
    ],
    "Chương 5: Phép cộng trong phạm vi 20": [
        "Bài 1: Cộng với số 0",
        "Bài 2: Cộng có nhớ",
        "Bài 3: Bảng cộng trong phạm vi 20",
        "Bài 4: Giải toán có lời văn"
    ],
    "Chương 6: Phép trừ trong phạm vi 20": [
        "Bài 1: Trừ với số 0",
        "Bài 2: Trừ có nhớ",
        "Bài 3: Bảng trừ trong phạm vi 20",
        "Bài 4: Giải toán có lời văn"
    ],
    "Chương 7: Hình học đơn giản": [
        "Bài 1: Hình tam giác",
        "Bài 2: Hình tứ giác",
        "Bài 3: Hình tròn",
        "Bài 4: Nhận biết các hình"
    ]
}

# Link ảnh mẫu theo chủ đề
image_links = {
    "Đếm": [
        "https://example.com/images/math/counting/img1.jpg",
        "https://example.com/images/math/counting/img2.jpg",
        "https://example.com/images/math/counting/img3.jpg",
        "https://example.com/images/math/counting/img4.jpg",
        "https://example.com/images/math/counting/img5.jpg"
    ],
    "Cộng": [
        "https://example.com/images/math/addition/img1.jpg",
        "https://example.com/images/math/addition/img2.jpg",
        "https://example.com/images/math/addition/img3.jpg",
        "https://example.com/images/math/addition/img4.jpg",
        "https://example.com/images/math/addition/img5.jpg"
    ],
    "Trừ": [
        "https://example.com/images/math/subtraction/img1.jpg",
        "https://example.com/images/math/subtraction/img2.jpg",
        "https://example.com/images/math/subtraction/img3.jpg",
        "https://example.com/images/math/subtraction/img4.jpg",
        "https://example.com/images/math/subtraction/img5.jpg"
    ],
    "So sánh": [
        "https://example.com/images/math/comparison/img1.jpg",
        "https://example.com/images/math/comparison/img2.jpg",
        "https://example.com/images/math/comparison/img3.jpg",
        "https://example.com/images/math/comparison/img4.jpg",
        "https://example.com/images/math/comparison/img5.jpg"
    ],
    "Hình học": [
        "https://example.com/images/math/geometry/img1.jpg",
        "https://example.com/images/math/geometry/img2.jpg",
        "https://example.com/images/math/geometry/img3.jpg",
        "https://example.com/images/math/geometry/img4.jpg",
        "https://example.com/images/math/geometry/img5.jpg"
    ]
}

# Các template câu hỏi và đáp án theo dạng bài
question_templates = {
    "Đếm đến 5": [
        {"template": "Hãy đếm số lượng {} trong hình và viết kết quả", "answer_template": "Có {} {}"},
        {"template": "Có bao nhiêu {} trong hình?", "answer_template": "Có {} {}"},
        {"template": "Nếu có {} {} trong hình, em hãy viết số đó", "answer_template": "Số đó là {}"}
    ],
    "Đếm đến 10": [
        {"template": "Hãy đếm số lượng {} trong hình và viết kết quả", "answer_template": "Có {} {}"},
        {"template": "Có bao nhiêu {} trong hình?", "answer_template": "Có {} {}"},
        {"template": "Nếu có {} {} trong hình, em hãy viết số đó", "answer_template": "Số đó là {}"}
    ],
    "Đếm đến 20": [
        {"template": "Hãy đếm số lượng {} trong hình và viết kết quả", "answer_template": "Có {} {}"},
        {"template": "Có bao nhiêu {} trong hình?", "answer_template": "Có {} {}"},
        {"template": "Nếu có {} {} trong hình, em hãy viết số đó", "answer_template": "Số đó là {}"}
    ],
    "So sánh": [
        {"template": "So sánh {} và {} bằng dấu >, <, =", "answer_template": "{} {} {}"},
        {"template": "Số nào lớn hơn: {} hay {}?", "answer_template": "{} lớn hơn {}"},
        {"template": "Số nào nhỏ hơn: {} hay {}?", "answer_template": "{} nhỏ hơn {}"}
    ],
    "Phép cộng": [
        {"template": "Tính: {} + {} = ?", "answer_template": "{} + {} = {}"},
        {"template": "Tìm tổng của {} và {}", "answer_template": "{} + {} = {}"},
        {"template": "{} cộng với {} bằng bao nhiêu?", "answer_template": "{} + {} = {}"}
    ],
    "Phép trừ": [
        {"template": "Tính: {} - {} = ?", "answer_template": "{} - {} = {}"},
        {"template": "Tìm hiệu của {} và {}", "answer_template": "{} - {} = {}"},
        {"template": "{} trừ đi {} bằng bao nhiêu?", "answer_template": "{} - {} = {}"}
    ],
    "Hình học": [
        {"template": "Hình nào trong hình là hình {}?", "answer_template": "Hình {} là hình số {}"},
        {"template": "Đếm số hình {} trong hình", "answer_template": "Có {} hình {}"},
        {"template": "Hình {} có mấy cạnh?", "answer_template": "Hình {} có {} cạnh"}
    ],
    "Lời văn cộng": [
        {"template": "{} có {} {}. {} được cho thêm {} {}. Hỏi {} có tất cả bao nhiêu {}?", "answer_template": "{} + {} = {}. Vậy {} có tất cả {} {}"},
        {"template": "Có {} {} và {} {}. Hỏi có tất cả bao nhiêu {}?", "answer_template": "{} + {} = {}. Vậy có tất cả {} {}"},
        {"template": "{} và {} có tổng cộng {} {}. {} có {} {}. Hỏi {} có bao nhiêu {}?", "answer_template": "{} - {} = {}. Vậy {} có {} {}"}
    ],
    "Lời văn trừ": [
        {"template": "{} có {} {}. {} đã cho đi {} {}. Hỏi {} còn lại bao nhiêu {}?", "answer_template": "{} - {} = {}. Vậy {} còn lại {} {}"},
        {"template": "Có {} {}. Đã lấy đi {} {}. Hỏi còn lại bao nhiêu {}?", "answer_template": "{} - {} = {}. Vậy còn lại {} {}"},
        {"template": "{} có {} {}. Sau khi dùng một số {}, {} còn lại {} {}. Hỏi {} đã dùng bao nhiêu {}?", "answer_template": "{} - {} = {}. Vậy {} đã dùng {} {}"}
    ]
}

# Đối tượng hình học
hinh_hoc_objects = {
    "tam giác": 3,
    "tứ giác": 4,
    "hình vuông": 4,
    "hình chữ nhật": 4,
    "hình tròn": 0
}

# Đối tượng đếm
objects = ["quả táo", "cái kẹo", "con chim", "quyển sách", "cái bút", "cái bàn", "cái ghế", "con mèo", "con chó", "quả cam", "bông hoa", "chiếc lá", "cây bút chì", "quả bóng", "chiếc ô", "con cá"]

# Các tên người
names = ["An", "Bình", "Cường", "Dung", "Hải", "Hoa", "Lan", "Mai", "Nam", "Phương", "Quang", "Thảo", "Tuấn", "Uyên", "Việt", "Xuân", "Yến"]

def get_image_link(bai_name):
    if "Đếm" in bai_name:
        return random.choice(image_links["Đếm"])
    elif "Cộng" in bai_name or "cộng" in bai_name:
        return random.choice(image_links["Cộng"])
    elif "Trừ" in bai_name or "trừ" in bai_name:
        return random.choice(image_links["Trừ"])
    elif "So sánh" in bai_name:
        return random.choice(image_links["So sánh"])
    elif "Hình" in bai_name:
        return random.choice(image_links["Hình học"])
    else:
        # Mặc định
        return random.choice(random.choice(list(image_links.values())))

def get_question_type(bai_name):
    if "Đếm đến 5" in bai_name:
        return "Đếm đến 5"
    elif "Đếm đến 10" in bai_name:
        return "Đếm đến 10"
    elif "Đếm đến 20" in bai_name:
        return "Đếm đến 20"
    elif "So sánh" in bai_name:
        return "So sánh"
    elif "Phép cộng" in bai_name or "Cộng" in bai_name:
        return "Phép cộng"
    elif "Phép trừ" in bai_name or "Trừ" in bai_name:
        return "Phép trừ"
    elif "Hình" in bai_name:
        return "Hình học"
    elif "lời văn" in bai_name.lower() and "cộng" in bai_name.lower():
        return "Lời văn cộng"
    elif "lời văn" in bai_name.lower() and "trừ" in bai_name.lower():
        return "Lời văn trừ"
    else:
        # Mặc định là phép cộng
        return "Phép cộng"

def generate_question_answer(question_type):
    template_data = question_templates.get(question_type, question_templates["Phép cộng"])
    template = random.choice(template_data)
    
    if question_type in ["Đếm đến 5", "Đếm đến 10", "Đếm đến 20"]:
        max_count = 5 if question_type == "Đếm đến 5" else (10 if question_type == "Đếm đến 10" else 20)
        count = random.randint(1, max_count)
        obj = random.choice(objects)
        
        # Kiểm tra số lượng tham số trong template
        if template["template"].count("{}") == 1:
            question = template["template"].format(obj)
        else:
            question = template["template"].format(count, obj)
            
        if template["answer_template"].count("{}") == 1:
            answer = template["answer_template"].format(count)
        else:
            answer = template["answer_template"].format(count, obj)
        
    elif question_type == "So sánh":
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        question = template["template"].format(a, b)
        
        if a > b:
            sign = ">"
            answer = template["answer_template"].format(a, sign, b)
        elif a < b:
            sign = "<"
            answer = template["answer_template"].format(a, sign, b)
        else:
            sign = "="
            answer = template["answer_template"].format(a, sign, b)
        
    elif question_type == "Phép cộng":
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        question = template["template"].format(a, b)
        answer = template["answer_template"].format(a, b, a + b)
        
    elif question_type == "Phép trừ":
        a = random.randint(5, 20)
        b = random.randint(1, a)
        question = template["template"].format(a, b)
        answer = template["answer_template"].format(a, b, a - b)
        
    elif question_type == "Hình học":
        hinh = random.choice(list(hinh_hoc_objects.keys()))
        position = random.randint(1, 5)
        
        if "cạnh" in template["template"]:
            question = template["template"].format(hinh)
            answer = template["answer_template"].format(hinh, hinh_hoc_objects[hinh])
        else:
            count = random.randint(1, 5)
            question = template["template"].format(hinh)
            answer = template["answer_template"].format(count, hinh) if "Đếm" in template["template"] else template["answer_template"].format(hinh, position)
            
    elif question_type == "Lời văn cộng":
        name1 = random.choice(names)
        name2 = random.choice([n for n in names if n != name1])
        obj = random.choice(objects)
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        
        if "tổng cộng" in template["template"]:
            question = template["template"].format(name1, name2, a + b, obj, name1, a, name2)
            answer = template["answer_template"].format(a + b, a, b, name2, b, obj)
        else:
            question = template["template"].format(name1, a, obj, name1, b, obj, name1, obj)
            answer = template["answer_template"].format(a, b, a + b, name1, a + b, obj)
        
    elif question_type == "Lời văn trừ":
        name = random.choice(names)
        obj = random.choice(objects)
        a = random.randint(5, 20)
        b = random.randint(1, a-1)
        
        if "Sau khi dùng" in template["template"]:
            question = template["template"].format(name, a, obj, name, a-b, obj, name, obj)
            answer = template["answer_template"].format(a, a-b, b, name, b, obj)
        else:
            question = template["template"].format(name, a, obj, name, b, obj, name, obj)
            answer = template["answer_template"].format(a, b, a-b, name, a-b, obj)
    
    else:
        # Default to addition
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        question = f"Tính: {a} + {b} = ?"
        answer = f"{a} + {b} = {a + b}"
    
    return question, answer

def generate_structured_data(n_entries=100):
    data = []
    
    for _ in range(n_entries):
        # Chọn ngẫu nhiên chương và bài
        chuong = random.choice(list(chuong_bai_structure.keys()))
        bai = random.choice(chuong_bai_structure[chuong])
        
        # Lấy loại câu hỏi dựa trên bài
        question_type = get_question_type(bai)
        
        # Tạo câu hỏi và đáp án
        question, answer = generate_question_answer(question_type)
        
        # Lấy link ảnh phù hợp
        image_link = get_image_link(bai)
        
        # Tạo cấu trúc dữ liệu
        entry = {
            "chuong": chuong,
            "bai": bai,
            "question": question,
            "answer": answer,
            "image_link": image_link
        }
        
        data.append(entry)
    
    return data

def save_data():
    data = generate_structured_data(100)  # Tạo 100 bản ghi theo yêu cầu
    # Tạo data directory nếu chưa tồn tại
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_qa_data_v1.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Đã tạo {len(data)} bản ghi dữ liệu có cấu trúc và lưu vào file math_qa_data_v1.json")

if __name__ == "__main__":
    save_data()