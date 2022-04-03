# Hệ thống xây dựng và tạo truyện đọc cho AppleBook

Có đôi khi ngẩn ngơ đọc một vài câu chuyện, hay vài cuốn sách tự biên tập.
Nhưng phảỉ mở máy tính lên thật bất tiện vì vậy hệ thống này được tạo ra
nhằm mục đích tạo truyện để đọc trên thiết bị AppleBook hoặc Kiddle

## Yêu cầu

Để có thể sử dụng được hệ thống máy phải được cài đặt tối thiểu như sau 

1. `python3+` nền tảng để chạy ứng dụng
2. `markdown` chuyển đổi nội dung Markdown text sang `HTML`

## Chạy ứng dụng

Có hai cách để tạo một là thủ công hai là thông qua dịch vụ được mở ở cổng
`9876` để gửi dữ liệu.

Để tạo thủ công chúng ta tạo thư mục `books` để lưu các truyện, và `epub`
để lưu các tập tin sau khi thành công.

### Đối với thao tác thủ công

Đầu tiên tạo thư mục chứa các chương của truyện vào thư mục `books` ví dụ
`books/Toi_Thay_Hoa_Vang_Tren_Co_Xanh`

Tham khảo tài liệu `Markdown` tại [đây](https://daringfireball.net/projects/markdown/)
rồi tiến hành viết các chương.

Tạo thêm tập tin `metadata.json` lưu vào thư mục chứa với nội dung sau

```JSON
{
  "metadata": {
    "dc:title": "",
    "dc:creator": "",
    "dc:language": "vi",
    "dc:identifier": "story_05283746-81ba-43cf-8dc8-2b45cb357dfb",
    "dc:source": "",
    "meta": "",
    "dc:date": "",
    "dc:publisher": "",
    "dc:contributor": "",
    "dc:rights": "",
    "dc:description": "",
    "dc:subject": ""
  },
  "cover": "cover.jpg",
  "chapters": [
    "intro.md",
    "chapter-1.md",
    "chapter-2.md"
  ]
}
```

Vài trường cơ bản trong tập tin `metadata.json` cần lưu ý

`dc:title` tên sách, `dc:creator` tác giả, `dc:identifier` id của sách không
trùng nhau, `chapters` lưu trữ các tập tin mà chúng ta đã viết nên sắp xếp.

### Đối với sử dụng dịch vụ

vui lòng tham khảo trong thư mục `scripts` có các tập tin `javascript` để
thực thi việc gửi dữ liệu lên cho hệ thống tự tạo

## Cài đặt

Tải bản git về dùng lệnh

```bash
git clone https://github.com/nhattn/All-Projects
```

Sao chép thư mục `All-Projects/dao-truyen` ra thư mục riêng sau đó tiến
hành cài đặt các yêu cầu cơ bản cho hệ thống

```bash
pip3 install -r requirements.txt
```

Để chạy dịch vụ sử dụng lệnh 

```bash
python3 service.py
```

Để tạo tập tin `epub` chạy lệnh

```bash
python3 md2epub.py <thu_muc_luu_tru>
```

Kết quả sẽ được tạo ra trong thư mục epub
