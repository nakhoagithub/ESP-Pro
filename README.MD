
# ESP32 + Module RS485 (Power by Anh Khoa)

Mã nguồn mở của ESP32 sử dụng làm module trung gian để điều khiển các thiết bị/relay của module sử dụng giao thức RS485, mã nguồn này được viết bằng ngôn ngữ Micropython và chạy trên ESP32 S3


### Phần cứng bắt buộc
- Yêu cầu [ESP32 S3](https://www.proe.vn/esp32-s3-microcontroller-2-4ghz-wi-fi-development-board-240mhz-dual-core-processor-esp32-s3-wroom-1-n8r8-module) (có thông số bằng hoặc cao hơn)

### Các chức năng
1. Kết nối Bluetooth và cấu hình thông qua [Serial Bluetooth Terminal](https://play.google.com/store/apps/details?id=de.kai_morich.serial_bluetooth_terminal)
2. Kết nối Wifi tạo Modbus TCP hoặc sử dụng [UART TTL to RS485](https://www.proe.vn/ttl-to-rs485-b) để tạo Modbus Serial
3. Kết nối điều khiển các module RS485
4. Đọc dữ liệu các cảm biến (RS485)

### Ứng dụng:
- Có thể dùng cho điều khiển tự động hóa và IoT - Smart Home

#

Đây là mã nguồn mở được viết bởi [Nguyễn Anh Khoa](https://github.com/nakhoagithub)

Phát hành ngày: 16/08/2024