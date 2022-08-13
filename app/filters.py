def play_opt(text):
    opt_text = {
            "runhi": "วิ่งบน",
            "runlo":"วิ่งล่าง",
            "3hi": "3 ตัวบน",
            "3lo": "3 ตัวล่าง",
            "2hi": "2 ตัวบน",
            "2lo": "2 ตัวล่าง",
            "swap3hi": "3 ตัวโต๊ดบน",
            "swap2hi": "2 ตัวโต๊ดบน",
            "swap2lo": "2 ตัวโต๊ดล่าง",
            "2hilo": "2 ตัวตรง",
            "swap": "โต๊ด"
            }
    return opt_text.get(text, text)
