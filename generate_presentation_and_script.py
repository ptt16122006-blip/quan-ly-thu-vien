import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

import docx
from docx.shared import Inches as DocxInches, Pt as DocxPt, RGBColor as DocxRGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# --- BẢNG MÀU THIẾT KẾ HIỆN ĐẠI (DARK LUXURY THEME) ---
BG_COLOR = RGBColor(15, 23, 42)        # Slate 900
HEADER_CARD = RGBColor(30, 41, 59)     # Slate 800
ACCENT_BLUE = RGBColor(56, 189, 248)   # Sky 400
ACCENT_CYAN = RGBColor(34, 211, 238)   # Cyan 400
TEXT_WHITE = RGBColor(248, 250, 252)   # Slate 50
TEXT_MUTED = RGBColor(148, 163, 184)   # Slate 400
CARD_BG = RGBColor(30, 41, 59)        # Slate 800
BORDER_COLOR = RGBColor(51, 65, 85)    # Slate 700

SLIDE_DATA = [
    {
        "slide_num": 1,
        "title": "HỆ THỐNG QUẢN LÝ THƯ VIỆN HIỆN ĐẠI",
        "subtitle": "Triển Khai Đa Dịch Vụ Với Docker Compose, Nginx SSL & Giám Sát Tập Trung",
        "badge": "ICTU • ĐỒ ÁN HỌC PHẦN",
        "bullets": [
            "Đề tài: Hệ Thống Quản Lý Thư Viện Đa Tầng An Toàn.",
            "Sinh viên: Phạm Tiến Toàn (Mã SV: DTC245200032).",
            "Giảng viên hướng dẫn: TS. Trần Quang Quý.",
            "Đóng gói 100% container hóa, vận hành với một lệnh duy nhất."
        ],
        "image": "DOC/slide_title_cover.png",
        "is_cover": True
    },
    {
        "slide_num": 2,
        "title": "TỔNG QUAN & CÔNG NGHỆ CỐT LÕI",
        "subtitle": "Kiến trúc đa tầng phục vụ quản lý thư viện số hóa toàn diện",
        "badge": "01. CÔNG NGHỆ",
        "bullets": [
            "FastAPI Microservice: Backend xử lý nhanh, phi đồng bộ, chuẩn RESTful.",
            "PostgreSQL 16: Cơ sở dữ liệu quan hệ mạnh mẽ, ACID, bảo vệ toàn vẹn.",
            "Nginx Ingress: Cổng tiếp nhận lưu lượng, cân bằng tải và điều hướng.",
            "Full Observability: Bộ đôi Prometheus thu thập metrics & Loki ghi nhận log."
        ],
        "image": "DOC/slide_tech_stack.png",
        "is_cover": False
    },
    {
        "slide_num": 3,
        "title": "KIẾN TRÚC HỆ THỐNG PHÂN TẦNG",
        "subtitle": "Topology 8 dịch vụ độc lập phân chia rõ ràng theo từng phân hệ",
        "badge": "02. KIẾN TRÚC",
        "bullets": [
            "Phân tầng Web & API: Nginx bảo vệ phía trước kết nối tới FastAPI Backend.",
            "Phân tầng Dữ liệu: PostgreSQL 16 và công cụ quản trị pgAdmin chuyên nghiệp.",
            "Phân tầng Giám sát: Prometheus lưu metrics thời gian thực & Grafana biểu đồ.",
            "Phân tầng Thu thập Nhật ký: Promtail gom log container và chuyển tiếp Loki."
        ],
        "image": "DOC/hinh_3_1_kien_truc_he_thong.png",
        "is_cover": False
    },
    {
        "slide_num": 4,
        "title": "CƠ CHẾ CÔ LẬP MẠNG AN TOÀN",
        "subtitle": "Nguyên tắc Least Exposure và phân vùng 3 mạng Docker bridge riêng biệt",
        "badge": "03. BẢO MẬT MẠNG",
        "bullets": [
            "frontend_network: Chỉ kết nối Nginx và App, tiếp nhận HTTP/HTTPS ngoài.",
            "backend_network: Vùng cách ly tuyệt đối cho PostgreSQL, không mở cổng 5432.",
            "monitoring_network: Đường truyền khép kín cho Prometheus, Loki & Grafana.",
            "Tuân thủ triệt để nguyên tắc đặc quyền tối thiểu (Least Privilege)."
        ],
        "image": "DOC/hinh_3_2_co_che_bao_mat_mang.png",
        "is_cover": False
    },
    {
        "slide_num": 5,
        "title": "QUY TRÌNH KỸ THUẬT 6 BƯỚC",
        "subtitle": "Quy trình triển khai chuẩn DevOps khép kín từ mã nguồn đến vận hành",
        "badge": "04. TRIỂN KHAI",
        "bullets": [
            "Bước 1 & 2: Xây dựng App FastAPI, Jinja2 ORM và container hóa PostgreSQL.",
            "Bước 3: Thiết lập Nginx Reverse Proxy, cấu hình SSL tự động và Headers an ninh.",
            "Bước 4: Tự động hóa kiểm tra cú pháp và khởi chạy bằng Docker Compose.",
            "Bước 5 & 6: Tích hợp giám sát chỉ số (Prometheus) và quản lý log tập trung (Loki)."
        ],
        "image": "DOC/hinh_4_1_quy_trinh_6_buoc.png",
        "is_cover": False
    },
    {
        "slide_num": 6,
        "title": "GIAO DIỆN & VẬN HÀNH THỰC TẾ",
        "subtitle": "Trải nghiệm người dùng mượt mà và trực quan hóa nghiệp vụ thư viện",
        "badge": "05. GIAO DIỆN & THỰC NGHIỆM",
        "bullets": [
            "Dashboard trực quan: Thống kê số lượng đầu sách, độc giả, phiếu mượn/trả.",
            "Nghiệp vụ đầy đủ: Tìm kiếm tức thì, mượn sách, gia hạn và hoàn trả thuận tiện.",
            "Bảo mật kết nối: Mã hóa HTTPS toàn trình, tự động redirect từ cổng 80 sang 443.",
            "Quản trị CSDL: Giao diện pgAdmin 4 trực quan hỗ trợ truy vấn và sao lưu."
        ],
        "image": "DOC/hinh_2_1_giao_dien_web.png",
        "is_cover": False
    },
    {
        "slide_num": 7,
        "title": "GIÁM SÁT HIỆU NĂNG VỚI PROMETHEUS & GRAFANA",
        "subtitle": "Theo dõi sát sao sức khỏe hệ thống thời gian thực theo chuỗi thời gian",
        "badge": "06. GIÁM SÁT HIỆU NĂNG",
        "bullets": [
            "FastAPI Endpoint /metrics: Xuất chỉ số request latency, throughput, mã lỗi.",
            "Postgres Exporter: Giám sát số connection, transaction rate, cache hit ratio.",
            "Grafana Dashboard: Biểu đồ trực quan, phân tích thời gian phản hồi đa chiều.",
            "Cảnh báo tức thì: Phát hiện sớm tải cao hoặc dấu hiệu bất thường của dịch vụ."
        ],
        "image": "DOC/hinh_5_1_giam_sat_metrics.png",
        "is_cover": False
    },
    {
        "slide_num": 8,
        "title": "QUẢN LÝ NHẬT KÝ TẬP TRUNG QUA LOKI & PROMTAIL",
        "subtitle": "Tra cứu, phân tích và xử lý sự cố nhanh chóng bằng ngôn ngữ LogQL",
        "badge": "07. NHẬT KÝ TẬP TRUNG",
        "bullets": [
            "Promtail Agent: Tự động đọc và gắn nhãn (labels) nhật ký qua Docker socket.",
            "Loki Server: Lưu trữ log hiệu năng cao, đánh chỉ mục theo nhãn siêu nhẹ.",
            "Truy vấn LogQL: Tra cứu nhật ký lỗi (5xx, 4xx) trực tiếp trên Grafana Explore.",
            "Không cần SSH từng container: Tiết kiệm 80% thời gian điều tra nguyên nhân gốc."
        ],
        "image": "DOC/hinh_6_1_truy_van_loki_logql.png",
        "is_cover": False
    },
    {
        "slide_num": 9,
        "title": "KẾT QUẢ ĐẠT ĐƯỢC & HƯỚNG PHÁT TRIỂN",
        "subtitle": "Khẳng định tính ổn định, độ an toàn và tiềm năng mở rộng của hệ thống",
        "badge": "08. KẾT LUẬN",
        "bullets": [
            "Đóng gói 100%: 8 dịch vụ phối hợp nhịp nhàng, kiểm thử vận hành thành công.",
            "An toàn CSDL: Không rò rỉ cổng 5432, phân tầng mạng cô lập vững chắc.",
            "Khả năng mở rộng: Sẵn sàng cấu hình Load Balancing và triển khai Kubernetes.",
            "Định hướng: Tích hợp xác thực JWT/OAuth2 và thông báo tự động trả sách."
        ],
        "image": "DOC/slide_achievements.png",
        "is_cover": False
    }
]

def build_powerpoint():
    prs = pptx.Presentation()
    # Tỉ lệ màn ảnh rộng 16:9
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    for s_idx, data in enumerate(SLIDE_DATA):
        slide = prs.slides.add_slide(blank_layout)
        
        # 1. Nền tối hiện đại (Dark Slate)
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        
        if data["is_cover"]:
            # Slide bìa: Thêm ảnh bìa lớn ở bên phải/toàn màn hình và chữ bên trái
            # Hình minh họa bìa
            if os.path.exists(data["image"]):
                slide.shapes.add_picture(data["image"], Inches(0.5), Inches(0.5), width=Inches(12.333), height=Inches(6.5))
            continue
            
        # 2. Header Bar / Top Banner
        header_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(0.4), Inches(12.133), Inches(1.1))
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = HEADER_CARD
        header_shape.line.color.rgb = BORDER_COLOR
        header_shape.line.width = Pt(1)
        
        # Badge nhỏ
        badge_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(5.0), Inches(0.25))
        tf_badge = badge_box.text_frame
        tf_badge.word_wrap = True
        p_badge = tf_badge.paragraphs[0]
        p_badge.text = data["badge"].upper()
        p_badge.font.size = Pt(10)
        p_badge.font.bold = True
        p_badge.font.color.rgb = ACCENT_CYAN
        
        # Tiêu đề slide
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.5), Inches(0.45))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = data["title"]
        p_title.font.size = Pt(18)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE
        
        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.15), Inches(11.5), Inches(0.3))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = data["subtitle"]
        p_sub.font.size = Pt(10.5)
        p_sub.font.color.rgb = ACCENT_BLUE
        
        # 3. Nội dung bên trái (Card Chứa Ý Chính / Bullet Points súc tích)
        left_card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.65), Inches(4.8), Inches(5.35))
        left_card.fill.solid()
        left_card.fill.fore_color.rgb = CARD_BG
        left_card.line.color.rgb = BORDER_COLOR
        left_card.line.width = Pt(1)
        
        # Tiêu đề nhóm ý chính
        key_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(4.4), Inches(0.4))
        p_key = key_box.text_frame.paragraphs[0]
        p_key.text = "TRỌNG TÂM CỐT LÕI"
        p_key.font.size = Pt(12)
        p_key.font.bold = True
        p_key.font.color.rgb = ACCENT_CYAN
        
        # Bullets
        bullets_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(4.4), Inches(4.6))
        tf_bullets = bullets_box.text_frame
        tf_bullets.word_wrap = True
        
        for b_idx, bullet in enumerate(data["bullets"]):
            p = tf_bullets.add_paragraph() if b_idx > 0 else tf_bullets.paragraphs[0]
            # Tách phần in đậm nếu có dấu hai chấm
            if ":" in bullet:
                parts = bullet.split(":", 1)
                r1 = p.add_run()
                r1.text = f"• {parts[0]}:"
                r1.font.bold = True
                r1.font.size = Pt(11.5)
                r1.font.color.rgb = ACCENT_BLUE
                
                r2 = p.add_run()
                r2.text = parts[1]
                r2.font.size = Pt(11)
                r2.font.color.rgb = TEXT_WHITE
            else:
                r = p.add_run()
                r.text = f"• {bullet}"
                r.font.size = Pt(11)
                r.font.color.rgb = TEXT_WHITE
            
            p.space_after = Pt(14)
            p.line_spacing = 1.2
            
        # 4. Nội dung bên phải (Hình ảnh minh họa trực quan nổi bật)
        img_card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.6), Inches(1.65), Inches(7.133), Inches(5.35))
        img_card.fill.solid()
        img_card.fill.fore_color.rgb = RGBColor(10, 16, 30)
        img_card.line.color.rgb = BORDER_COLOR
        img_card.line.width = Pt(1)
        
        if os.path.exists(data["image"]):
            # Chèn ảnh minh họa vừa khít khung
            slide.shapes.add_picture(data["image"], Inches(5.7), Inches(1.75), width=Inches(6.933), height=Inches(5.15))
            
        # Số trang ở góc dưới bên phải
        page_box = slide.shapes.add_textbox(Inches(12.0), Inches(7.05), Inches(1.0), Inches(0.3))
        p_page = page_box.text_frame.paragraphs[0]
        p_page.text = f"{data['slide_num']} / {len(SLIDE_DATA)}"
        p_page.font.size = Pt(9)
        p_page.font.color.rgb = TEXT_MUTED
        p_page.alignment = PP_ALIGN.RIGHT

    pptx_path = "DOC/SLIDE_THUYET_TRINH_QUAN_LY_THU_VIEN.pptx"
    prs.save(pptx_path)
    print(f"PowerPoint đã được tạo thành công tại: {pptx_path}")

# --- SOẠN KỊCH BẢN THUYẾT TRÌNH BẰNG WORD (.DOCX) ---
SPEAKING_SCRIPTS = [
    {
        "slide_num": 1,
        "title": "Slide 1: Trang Bìa - Giới Thiệu Đề Tài",
        "duration": "Thời lượng dự kiến: 1 phút",
        "speech": (
            "Kính thưa Thầy giáo TS. Trần Quang Quý và toàn thể các bạn học viên trong hội đồng.\n\n"
            "Hôm nay, em xin phép được đại diện trình bày đồ án học phần với đề tài: "
            "\"Hệ Thống Quản Lý Thư Viện trên nền tảng Docker Compose, Nginx Reverse Proxy và Hệ Thống Giám Sát Tập Trung\".\n\n"
            "Em là Phạm Tiến Toàn, học viên lớp CNTT, mã số sinh viên DTC245200032. "
            "Đồ án được nghiên cứu và hiện thực dưới sự hướng dẫn chuyên môn trực tiếp của TS. Trần Quang Quý. "
            "Mục tiêu cốt lõi của đề tài là áp dụng chuẩn kiến trúc DevOps hiện đại để giải quyết bài toán quản trị thư viện số hóa: "
            "đóng gói hoàn chỉnh thành các vi dịch vụ (Microservices), cô lập bảo mật cơ sở dữ liệu và xây dựng hệ thống giám sát thời gian thực toàn diện. "
            "Sau đây, em xin kính mời Thầy và các bạn cùng đi vào nội dung chi tiết của từng phần."
        ),
        "tips": "Nói to, rõ ràng, phong thái tự tin. Dành ánh mắt hướng về giảng viên và hội đồng khi giới thiệu thông tin cá nhân và đề tài."
    },
    {
        "slide_num": 2,
        "title": "Slide 2: Tổng Quan Bài Toán & Công Nghệ Cốt Lõi",
        "duration": "Thời lượng dự kiến: 1.5 phút",
        "speech": (
            "Thưa Thầy và các bạn, bước sang slide thứ hai, em xin giới thiệu bài toán thực tế và các công nghệ cốt lõi được lựa chọn.\n\n"
            "Trước đây, các hệ thống thư viện truyền thống thường gặp 3 thách thức lớn: "
            "Thứ nhất là khó khăn trong việc cài đặt, xung đột môi trường runtime khi nâng cấp; "
            "Thứ hai là nguy cơ rò rỉ dữ liệu khi cơ sở dữ liệu mở cổng kết nối trực tiếp ra ngoài Internet; "
            "Thứ ba là thiếu công cụ giám sát, chỉ khi hệ thống gặp sự cố người quản trị mới phát hiện.\n\n"
            "Để khắc phục triệt để, hệ thống của chúng em được xây dựng trên 4 trụ cột công nghệ vững chắc:\n"
            "- Backend sử dụng Python FastAPI kết hợp Jinja2: Mang lại tốc độ phản hồi cực nhanh, xử lý bất đồng bộ chuẩn mực và phục vụ giao diện người dùng nhẹ nhàng.\n"
            "- Cơ sở dữ liệu sử dụng PostgreSQL 16 Alpine: Đảm bảo tính toàn vẹn dữ liệu chuẩn ACID, đồng thời tối ưu hóa dung lượng bộ nhớ.\n"
            "- Nginx Ingress: Đóng vai trò Reverse Proxy, điểm tiếp nhận lưu lượng duy nhất từ bên ngoài, tự động cấu hình HTTPS và bảo vệ các dịch vụ phía trong.\n"
            "- Bộ đôi Prometheus và Grafana, Loki: Cung cấp giải pháp Full Observability, thu thập cả chỉ số hiệu năng (Metrics) lẫn nhật ký hoạt động (Logs) theo thời gian thực."
        ),
        "tips": "Nhấn mạnh vào 4 khối công nghệ hiện trên slide để người nghe thấy rõ tính chọn lọc và mục đích kỹ thuật của từng công nghệ."
    },
    {
        "slide_num": 3,
        "title": "Slide 3: Kiến Trúc Phân Tầng Hệ Thống (Topology 8 Dịch Vụ)",
        "duration": "Thời lượng dự kiến: 1.5 phút",
        "speech": (
            "Tại slide số 3, em xin trình bày về Kiến trúc phân tầng và sơ đồ Topology của toàn bộ hệ thống.\n\n"
            "Hệ thống không triển khai theo dạng nguyên khối (Monolith) mà được module hóa hoàn toàn thành 8 dịch vụ container độc lập, phân thành 4 tầng nghiệp vụ rõ rệt:\n"
            "1. Tầng Ingress & Web: Đứng đầu là Nginx Reverse Proxy tiếp nhận các request trên cổng 80 và 443, sau đó điều hướng thông minh đến ứng dụng web FastAPI.\n"
            "2. Tầng Ứng dụng & Dịch vụ: Container FastAPI chạy ứng dụng Quản lý Thư viện dưới quyền người dùng non-root (appuser) nhằm ngăn chặn việc leo thang đặc quyền nếu xảy ra tấn công mã nguồn.\n"
            "3. Tầng Dữ liệu: Gồm cơ sở dữ liệu PostgreSQL 16 và giao diện quản trị pgAdmin 4. pgAdmin cho phép quản trị viên xem xét bảng biểu, sao lưu dữ liệu mà không cần truy cập console máy chủ.\n"
            "4. Tầng Giám sát & Quan sát (Observability): Gồm Prometheus, Grafana, Postgres Exporter, Promtail và Loki. Tất cả phối hợp chặt chẽ tạo thành một hệ sinh thái giám sát khép kín.\n\n"
            "Mỗi container đều có giới hạn tài nguyên và cấu hình Healthcheck tự động nhằm đảm bảo tính sẵn sàng cao."
        ),
        "tips": "Chỉ tay vào sơ đồ phân tầng trực quan trên slide để người nghe dễ hình dung luồng dữ liệu từ trái sang phải, từ ngoài vào trong."
    },
    {
        "slide_num": 4,
        "title": "Slide 4: Cơ Chế Cô Lập Mạng An Toàn (Network Isolation)",
        "duration": "Thời lượng dự kiến: 1.5 phút",
        "speech": (
            "Tiếp theo tại slide số 4, đây là một trong những điểm sáng kỹ thuật quan trọng nhất của đồ án: 'Cơ chế cô lập mạng an toàn và nguyên tắc Least Privilege'.\n\n"
            "Chúng em không sử dụng mạng mặc định (default bridge) của Docker vì điều đó cho phép tất cả các container giao tiếp tự do với nhau. Thay vào đó, hệ thống được phân chia thành 3 mạng bridge cô lập tuyệt đối:\n"
            "- Thứ nhất là frontend_network: Mạng này chỉ bao gồm Nginx và App FastAPI. Người dùng bên ngoài chỉ có thể nhìn thấy cổng 80 và 443 của Nginx.\n"
            "- Thứ hai là backend_network: Mạng nội bộ tuyệt mật, kết nối giữa App, PostgreSQL, pgAdmin và Postgres Exporter. Đặc biệt, cổng 5432 của PostgreSQL hoàn toàn KHÔNG được expose ra máy host. Hacker dù có dò quét cổng từ ngoài Internet cũng không thể thấy hay tấn công trực tiếp vào cơ sở dữ liệu.\n"
            "- Thứ ba là monitoring_network: Mạng giám sát chuyên dụng, kết nối Prometheus, Grafana, Loki và Promtail để thu thập dữ liệu nội bộ mà không làm ảnh hưởng đến lưu lượng của người dùng truy cập web.\n\n"
            "Cơ chế này áp dụng đúng chuẩn phòng thủ theo chiều sâu (Defense-in-depth) trong quản trị hạ tầng hiện đại."
        ),
        "tips": "Nhấn mạnh cụm từ 'Không expose cổng 5432' - đây là tiêu chuẩn bảo mật được các giảng viên đánh giá rất cao."
    },
    {
        "slide_num": 5,
        "title": "Slide 5: Quy Trình Kỹ Thuật 6 Bước Triển Khai",
        "duration": "Thời lượng dự kiến: 1 phút",
        "speech": (
            "Kính thưa Thầy, để hiện thực hóa kiến trúc phức tạp trên, toàn bộ đồ án được thực hiện theo quy trình kỹ thuật 6 bước chuẩn hóa như trên sơ đồ:\n\n"
            "- Bước 1: Phát triển mã nguồn ứng dụng Thư viện với FastAPI, xây dựng ORM và thiết kế giao diện Jinja2 thân thiện.\n"
            "- Bước 2: Container hóa hệ quản trị PostgreSQL, cấu hình Persistent Volume để lưu trữ dữ liệu bền vững và triển khai pgAdmin.\n"
            "- Bước 3: Thiết lập Nginx Reverse Proxy, tạo chứng chỉ SSL, cấu hình tự động chuyển hướng HTTP sang HTTPS và bổ sung các header an ninh như X-Frame-Options, X-Content-Type-Options.\n"
            "- Bước 4: Viết file docker-compose.yml thống nhất, kiểm tra cú pháp và tự động hóa khởi động toàn bộ 8 container bằng một lệnh duy nhất.\n"
            "- Bước 5: Cấu hình Prometheus Exporter để cào (scrape) các chỉ số hiệu năng và trực quan hóa lên Grafana Dashboard.\n"
            "- Bước 6: Xây dựng hệ thống thu thập log tập trung với Promtail và Loki, loại bỏ hoàn toàn thao tác thủ công kiểm tra log trên máy chủ."
        ),
        "tips": "Nói ngắn gọn, dứt khoát từng bước để chứng minh đồ án có lộ trình phát triển bài bản, chặt chẽ."
    },
    {
        "slide_num": 6,
        "title": "Slide 6: Giao Diện Người Dùng & Vận Hành Thực Tế",
        "duration": "Thời lượng dự kiến: 1 phút",
        "speech": (
            "Trên slide số 6 là hình ảnh thực tế của Website Quản lý Thư viện khi người dùng truy cập qua giao diện Nginx an toàn (HTTPS).\n\n"
            "Hệ thống cung cấp đầy đủ các phân hệ nghiệp vụ:\n"
            "- Bảng điều khiển (Dashboard) thống kê tổng quan: Cho biết ngay số lượng đầu sách hiện có, tổng số độc giả và số phiếu đang mượn/chưa trả.\n"
            "- Nghiệp vụ quản lý sách: Cho phép tìm kiếm sách theo tên, tác giả, thể loại với tốc độ phản hồi tính bằng mili-giây; hỗ trợ thêm, sửa, cập nhật số lượng tồn kho.\n"
            "- Nghiệp vụ mượn - trả sách: Ghi nhận độc giả, ngày mượn, hạn trả và tự động tính toán số sách còn lại trên kệ.\n"
            "- Về trải nghiệm bảo mật: Khi người dùng gõ http://localhost, Nginx lập tức trả về mã lỗi 301 chuyển hướng tự động sang https://localhost, đồng thời khóa bảo vệ bằng giao thức SSL."
        ),
        "tips": "Chỉ vào các thẻ thống kê (Thống kê sách, độc giả, phiếu mượn) trên ảnh để chứng minh ứng dụng chạy thật, dữ liệu thật."
    },
    {
        "slide_num": 7,
        "title": "Slide 7: Hệ Thống Giám Sát Hiệu Năng (Prometheus & Grafana)",
        "duration": "Thời lượng dự kiến: 1.5 phút",
        "speech": (
            "Ở slide số 7, chúng em minh họa trực tiếp Bảng điều khiển giám sát hiệu năng trên Grafana.\n\n"
            "Như Thầy và các bạn thấy trên màn hình:\n"
            "- Ứng dụng FastAPI đã được tích hợp thư viện Prometheus Client, định kỳ xuất dữ liệu tại endpoint nội bộ /metrics.\n"
            "- Prometheus server cứ mỗi 5 giây sẽ thực hiện scrape dữ liệu này, cùng với chỉ số phần cứng và số lượng kết nối cơ sở dữ liệu từ Postgres Exporter.\n"
            "- Trên Grafana Dashboard, quản trị viên có thể theo dõi trực tiếp các biểu đồ chuỗi thời gian như: Tỷ lệ sử dụng CPU/RAM, Số lượng request/giây (RPS), Độ trễ trung bình (Latency p95, p99), và Tỷ lệ thành công của các request.\n"
            "Nhờ vậy, khi hệ thống bị nghẽn cổ chai hoặc có dấu hiệu quá tải, quản trị viên sẽ phát hiện được ngay lập tức thay vì phải chờ người dùng phản ánh."
        ),
        "tips": "Nói thêm về tần suất cào dữ liệu (5s/lần) và khả năng quan sát độ trễ để làm nổi bật chiều sâu kỹ thuật."
    },
    {
        "slide_num": 8,
        "title": "Slide 8: Quản Lý Nhật Ký Tập Trung Với Loki & Promtail",
        "duration": "Thời lượng dự kiến: 1.5 phút",
        "speech": (
            "Slide số 8 trình bày về Hệ thống quản lý nhật ký tập trung sử dụng bộ công nghệ Promtail và Grafana Loki.\n\n"
            "Trước đây, mỗi khi muốn xem lỗi, người quản trị phải SSH vào máy chủ và gõ lệnh xem log cho từng container riêng rẽ rất mất thời gian. Giờ đây:\n"
            "- Promtail hoạt động như một daemon ngầm, tự động kết nối qua Docker socket (/var/run/docker.sock) để thu thập log từ tất cả các container đang chạy.\n"
            "- Các dòng log được chuẩn hóa, gắn nhãn (như container_name, service, level) và đẩy về Loki server.\n"
            "- Trên giao diện Grafana Explore, chúng em chỉ cần viết các câu truy vấn bằng ngôn ngữ LogQL ngắn gọn, ví dụ: {service=\"app\"} |= \"ERROR\" là có thể lọc ra chính xác các ngoại lệ, lỗi phát sinh kèm theo mốc thời gian chi tiết.\n"
            "Giải pháp này giúp rút ngắn hơn 80% thời gian điều tra và khoanh vùng sự cố cho đội ngũ vận hành."
        ),
        "tips": "Giải thích ngắn gọn ý nghĩa của câu truy vấn LogQL hiển thị trên hình ảnh minh họa."
    },
    {
        "slide_num": 9,
        "title": "Slide 9: Kết Luận & Hướng Phát Triển Đề Tài",
        "duration": "Thời lượng dự kiến: 1 phút",
        "speech": (
            "Để khép lại bài thuyết trình, tại slide số 9, em xin tổng kết các thành quả đã đạt được của đồ án:\n\n"
            "1. Về mặt vận hành: Đã đóng gói thành công 100% hệ sinh thái 8 dịch vụ vào Docker Compose. Bất kỳ ai cũng có thể triển khai dự án trong chưa đầy 2 phút chỉ với một câu lệnh duy nhất.\n"
            "2. Về mặt bảo mật: Đã hiện thực hóa kiến trúc cô lập 3 mạng riêng ảo, giấu kín hoàn toàn cơ sở dữ liệu PostgreSQL và bảo vệ lưu lượng bằng Nginx HTTPS với SSL.\n"
            "3. Về mặt giám sát: Đạt chuẩn Observability với sự kết hợp hoàn hảo giữa Prometheus (Metrics) và Loki (Logs).\n\n"
            "Về hướng phát triển trong tương lai, nhóm dự kiến mở rộng mô hình sang cụm Kubernetes để tự động co giãn (Autoscaling), bổ sung cơ chế xác thực tập trung OAuth2/JWT và tính năng nhắc nhở trả sách tự động qua Email.\n\n"
            "Em xin chân thành cảm ơn TS. Trần Quang Quý và hội đồng đã chú ý lắng nghe bài thuyết trình. Em rất mong nhận được những nhận xét, góp ý quý báu của Thầy để hoàn thiện đề tài hơn nữa. Em xin trân trọng cảm ơn!"
        ),
        "tips": "Cúi đầu nhẹ chào hội đồng, giữ nét mặt tươi vui, sẵn sàng chuyển sang phần trả lời câu hỏi phản biện."
    }
]

def build_word_document():
    doc = docx.Document()
    
    # Thiết lập lề chuẩn văn bản học thuật (A4)
    for section in doc.sections:
        section.top_margin = DocxInches(1.0)
        section.bottom_margin = DocxInches(1.0)
        section.left_margin = DocxInches(1.0)
        section.right_margin = DocxInches(1.0)
        
    # Tiêu đề tài liệu Word
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("KỊCH BẢN THUYẾT TRÌNH BẢO VỆ ĐỒ ÁN HỌC PHẦN")
    run_title.font.name = "Arial"
    run_title.font.size = DocxPt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = DocxRGBColor(15, 23, 42)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run("ĐỀ TÀI: HỆ THỐNG QUẢN LÝ THƯ VIỆN TRÊN NỀN TẢNG DOCKER COMPOSE, NGINX VÀ GIÁM SÁT TẬP TRUNG\n")
    run_sub.font.name = "Arial"
    run_sub.font.size = DocxPt(12)
    run_sub.font.bold = True
    run_sub.font.color.rgb = DocxRGBColor(2, 132, 199)
    
    # Bảng thông tin sinh viên & giảng viên
    table = doc.add_table(rows=2, cols=2)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Sinh viên thực hiện: Phạm Tiến Toàn"
    hdr_cells[1].text = "Mã sinh viên: DTC245200032"
    row2_cells = table.rows[1].cells
    row2_cells[0].text = "Giảng viên hướng dẫn: TS. Trần Quang Quý"
    row2_cells[1].text = "Thời lượng thuyết trình: 10 - 12 phút (9 Trang)"
    
    doc.add_paragraph() # Spacing
    
    # Lời dặn trước khi thuyết trình
    p_note = doc.add_paragraph()
    r_nh = p_note.add_run("LƯU Ý DÀNH CHO NGƯỜI THUYẾT TRÌNH:\n")
    r_nh.bold = True
    r_nh.font.color.rgb = DocxRGBColor(225, 29, 72)
    p_note.add_run(
        "• Bài PowerPoint được thiết kế chuẩn tỉ lệ 16:9 với phong cách trực quan (ít chữ, nhiều hình ảnh và biểu đồ kiến trúc).\n"
        "• Toàn bộ lời thoại chi tiết được soạn theo từng slide dưới đây. Bạn chỉ cần đọc hoặc nắm các ý chính để nói một cách tự nhiên nhất.\n"
        "• Hãy kết hợp vừa nói vừa chỉ vào các hình minh họa tương ứng trên màn chiếu để đạt điểm đánh giá cao nhất."
    )
    doc.add_paragraph()
    
    # Duyệt từng slide và sinh kịch bản chi tiết
    for item in SPEAKING_SCRIPTS:
        # Tiêu đề slide
        h = doc.add_heading(level=1)
        r_h = h.add_run(item["title"])
        r_h.font.name = "Arial"
        r_h.font.size = DocxPt(14)
        r_h.font.bold = True
        r_h.font.color.rgb = DocxRGBColor(30, 58, 138)
        
        # Thời lượng
        p_dur = doc.add_paragraph()
        r_dur = p_dur.add_run(f"⏱ {item['duration']}")
        r_dur.font.italic = True
        r_dur.font.size = DocxPt(10)
        r_dur.font.color.rgb = DocxRGBColor(100, 116, 139)
        
        # Lời thoại chi tiết
        p_sp = doc.add_paragraph()
        r_lbl = p_sp.add_run("Lời thoại thuyết trình (Script chi tiết):\n")
        r_lbl.font.bold = True
        r_lbl.font.color.rgb = DocxRGBColor(15, 23, 42)
        
        r_speech = p_sp.add_run(item["speech"])
        r_speech.font.size = DocxPt(11)
        p_sp.paragraph_format.line_spacing = 1.25
        
        # Mẹo thuyết trình
        p_tip = doc.add_paragraph()
        r_tip_lbl = p_tip.add_run("💡 Mẹo trình bày & Tương tác hình ảnh: ")
        r_tip_lbl.font.bold = True
        r_tip_lbl.font.color.rgb = DocxRGBColor(13, 148, 136)
        
        r_tip_val = p_tip.add_run(item["tips"])
        r_tip_val.font.size = DocxPt(10.5)
        r_tip_val.font.italic = True
        
        doc.add_paragraph() # Spacing between slides
        
    docx_path = "DOC/KICH_BAN_THUYET_TRINH_QUAN_LY_THU_VIEN.docx"
    doc.save(docx_path)
    print(f"File Word kịch bản thuyết trình đã được tạo thành công tại: {docx_path}")

if __name__ == "__main__":
    build_powerpoint()
    build_word_document()
