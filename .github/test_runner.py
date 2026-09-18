import os
import re
import subprocess
import sys


def normalize_text(text):
    """ตัดสัญลักษณ์ ตัวพิมพ์เล็ก-ใหญ่ และเว้นวรรคส่วนเกิน"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[!.,:="\'\(\)]', " ", text)
    return " ".join(text.split())


def extract_numbers(text):
    """ดึงตัวเลขทั้งหมดจากผลลัพธ์ของนักเรียน"""
    if not text:
        return []
    return [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", text)]


def run_student_code(filename, input_data):
    """สั่งรันโค้ดนักเรียน รองรับทั้งมีและไม่มี .py"""
    target_file = filename
    if not os.path.exists(target_file) and not target_file.endswith(".py"):
        target_file = filename + ".py"

    if not os.path.exists(target_file):
        return None, "File Not Found"

    try:
        process = subprocess.run(
            [sys.executable, target_file],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=5,
        )
        return process.stdout, process.stderr
    except subprocess.TimeoutExpired:
        return None, "Timeout (โปรแกรมวนลูปไม่จบ)"
    except Exception as e:
        return None, str(e)


# =========================================================
# เกณฑ์การตรวจยืดหยุ่นแยกรายข้อสำหรับ Set 2 (ข้อละ 4 คะแนน)
# =========================================================


def grade_exam_1(output, stderr, test_case):
    """ข้อ 1: แปลงอุณหภูมิ C -> F [สูตร F = (C * 1.8) + 32]"""
    expected = test_case["expected"]
    c = test_case["c"]
    nums = extract_numbers(output)

    if any(abs(n - expected) < 0.1 for n in nums):
        return 1.0  # คำนวณถูกต้องได้เต็ม
    elif any(abs(n - (c * 1.8)) < 0.1 for n in nums) or any(
        abs(n - (c + 32)) < 0.1 for n in nums
    ):
        return 0.5  # คำนวณสูตรผิดบางส่วน (เช่น ลืม +32 หรือ ลืม *1.8)
    elif len(nums) > 0:
        return 0.25  # มีการแสดงผลตัวเลขออกมา
    return 0.0


def grade_exam_2(output, stderr, test_case):
    """ข้อ 2: ตรวจสิทธิ์เลือกตั้ง (Eligible / Not Eligible)"""
    expected = test_case["expected"].lower()
    norm_out = normalize_text(output)

    if expected == "not eligible":
        if "not" in norm_out and "eligible" in norm_out:
            return 1.0  # พิมพ์คำว่า Not Eligible ถูกต้อง (ไม่ซีเรียสเรื่องเว้นวรรค/พิมพ์เล็กใหญ่)
    elif expected == "eligible":
        if "eligible" in norm_out and "not" not in norm_out:
            return 1.0  # พิมพ์ Eligible ถูกต้อง

    if "eligible" in norm_out:
        return 0.5  # แสดงคำตอบกลุ่มสิทธิ์เลือกตั้งออกมาได้
    return 0.0


def grade_exam_3(output, stderr, test_case):
    """ข้อ 3: จำนวนบวก / จำนวนลบ (Positive / Negative)"""
    expected = test_case["expected"].lower()
    norm_out = normalize_text(output)

    if expected in norm_out:
        return 1.0  # พิมพ์ Positive/Negative ถูกต้อง
    elif "positive" in norm_out or "negative" in norm_out:
        return 0.5  # พิมพ์ประเภทคำตอบออกมาได้แต่เงื่อนไขสลับกัน
    return 0.0


def grade_exam_4(output, stderr, test_case):
    """ข้อ 4: คำนวณราคาสินค้าหลังหักส่วนลด"""
    expected = test_case["expected"]
    original_price = test_case["price"]
    discount = test_case["discount"]
    nums = extract_numbers(output)

    if any(abs(n - expected) < 0.1 for n in nums):
        return 1.0  # คำนวณราคาสุทธิถูกต้อง
    elif any(abs(n - original_price) < 0.1 for n in nums) or any(
        abs(n - discount) < 0.1 for n in nums
    ):
        return 0.5  # พิมพ์ราคาเดิมก่อนลด หรือพิมพ์เฉพาะยอดส่วนลดออกมา
    elif len(nums) > 0:
        return 0.25  # มีการแสดงผลตัวเลขออกมา
    return 0.0


def grade_exam_5(output, stderr, test_case):
    """ข้อ 5: ประเมินความเร็วรถยนต์ (Normal / Fast / Too Fast)"""
    expected = test_case["expected"].lower()
    norm_out = normalize_text(output)

    if expected == "too fast":
        if "too" in norm_out and "fast" in norm_out:
            return 1.0
    elif expected == "fast":
        if "fast" in norm_out and "too" not in norm_out:
            return 1.0
    elif expected == "normal":
        if "normal" in norm_out:
            return 1.0

    if any(k in norm_out for k in ["normal", "fast", "too"]):
        return 0.5  # พิมพ์สถานะความเร็วตัวใดตัวหนึ่งออกมาได้
    return 0.0


# =========================================================
# ชุดข้อมูลทดสอบ (Test Cases สำหรับ Set 2)
# =========================================================
EXAMS = {
    "Examination_1.py": {
        "grader": grade_exam_1,
        "cases": [
            {"input": "0\n", "expected": 32.0, "c": 0},
            {"input": "100\n", "expected": 212.0, "c": 100},
            {"input": "25\n", "expected": 77.0, "c": 25},
            {"input": "-40\n", "expected": -40.0, "c": -40},
        ],
    },
    "Examination_2.py": {
        "grader": grade_exam_2,
        "cases": [
            {"input": "20\n", "expected": "Eligible"},
            {"input": "18\n", "expected": "Eligible"},
            {"input": "17\n", "expected": "Not Eligible"},
            {"input": "10\n", "expected": "Not Eligible"},
        ],
    },
    "Examination_3.py": {
        "grader": grade_exam_3,
        "cases": [
            {"input": "5\n", "expected": "Positive"},
            {"input": "0\n", "expected": "Positive"},
            {"input": "-10\n", "expected": "Negative"},
            {"input": "-1\n", "expected": "Negative"},
        ],
    },
    "Examination_4.py": {
        "grader": grade_exam_4,
        "cases": [
            {
                "input": "2500\n",
                "expected": 2300,
                "price": 2500,
                "discount": 200,
            },
            {
                "input": "2000\n",
                "expected": 1800,
                "price": 2000,
                "discount": 200,
            },
            {
                "input": "1500\n",
                "expected": 1400,
                "price": 1500,
                "discount": 100,
            },
            {"input": "800\n", "expected": 800, "price": 800, "discount": 0},
        ],
    },
    "Examination_5.py": {
        "grader": grade_exam_5,
        "cases": [
            {"input": "50\n", "expected": "Normal"},
            {"input": "60\n", "expected": "Normal"},
            {"input": "80\n", "expected": "Fast"},
            {"input": "100\n", "expected": "Too Fast"},
        ],
    },
}

# =========================================================
# ประมวลผลและสร้าง Markdown สรุปคะแนน
# =========================================================
total_score = 0.0
summary_rows = []

for exam_name, exam_data in EXAMS.items():
    grader = exam_data["grader"]
    cases = exam_data["cases"]

    exam_score = 0.0
    passed_cases = 0.0

    for case in cases:
        stdout, stderr = run_student_code(exam_name, case["input"])
        if stdout is not None:
            score = grader(stdout, stderr, case)
            exam_score += score
            if score >= 1.0:
                passed_cases += 1.0
            elif score > 0:
                passed_cases += 0.5

    final_exam_score = min(4.0, round(exam_score, 1))
    total_score += final_exam_score

    if final_exam_score >= 4.0:
        status = "🟢 ผ่าน"
    elif final_exam_score > 0:
        status = "🟡 ผ่านบางส่วน"
    else:
        status = "❌ ไม่ผ่าน"

    score_display = (
        f"{int(final_exam_score)}"
        if final_exam_score.is_integer()
        else f"{final_exam_score}"
    )
    passed_display = (
        f"{int(passed_cases)}"
        if passed_cases.is_integer()
        else f"{passed_cases}"
    )

    summary_rows.append(
        f"| `{exam_name}` | {status} | {passed_display}/4 เคส | {score_display} / 4 |"
    )

final_total_display = (
    f"{int(total_score)}" if total_score.is_integer() else f"{total_score}"
)

markdown_summary = f"""
## 📊 สรุปผลการสอบวิชาเขียนโปรแกรม (Set 2)

| ข้อสอบ | สถานะการตรวจ | ผ่าน Test Cases | คะแนนที่ได้ |
| :--- | :--- | :--- | :--- |
""" + "\n".join(summary_rows) + f"""

### 🎯 คะแนนรวมทั้งหมด: {final_total_display} / 20 คะแนน
"""

print(markdown_summary)

github_summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
if github_summary_path:
    with open(github_summary_path, "a", encoding="utf-8") as f:
        f.write(markdown_summary)
