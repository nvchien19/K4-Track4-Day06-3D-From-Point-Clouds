# Trình bày 3 phút — Topic A

**Nguyễn Văn Chiến — 2A202602926**

## 0:00–0:40 — Câu hỏi và pipeline

Tôi kiểm tra calibration LiDAR-camera khi giá đỡ bị lệch yaw. Pipeline chuyển điểm bằng `R0_rect @ Tr_velo_to_cam`, chiếu bằng `P2`, chia tọa độ đồng nhất rồi loại điểm NaN/Inf, sau camera và ngoài ảnh. Điểm chuẩn `(10,0,0)` cho depth 9.727 m và pixel khoảng `(614,175)`.

## 0:40–1:30 — Thí nghiệm và số liệu

Mở `results/figures/yaw_perturb_sweep.png`. Trên synthetic frame `000000`, giữ nguyên dữ liệu và box, chỉ thay yaw 0°, 0.5°, 1°, 2°, 3°. Tỷ lệ điểm trong hợp các 2D box giảm từ 35.243% xuống 29.605%, tức 5.64 điểm phần trăm. Tỷ lệ điểm trong ảnh tăng nhẹ từ 16.339% lên 16.699%. Chạy hai lần trên Colab cho CSV giống hệt nhau.

## 1:30–2:20 — Failure và giới hạn metric

Mở baseline và `results/figures/fail_01_yaw_3deg_000000.png`: điểm ở cột, xe và người bị lệch khỏi vị trí ảnh. Nguyên nhân thuộc Geometry vì extrinsic bị perturb. Monitor chỉ dùng tỷ lệ FOV không phát hiện được drift này. Tỷ lệ điểm trong 2D box chỉ là proxy: có thể đếm điểm nền, không phải recall detector.

## 2:20–3:00 — Ứng dụng và bước tiếp theo

Trong ADAS, kiểm tra alignment sau bảo dưỡng/va chạm; ghi log điểm hợp lệ, FOV và edge/box alignment qua nhiều frame. Chưa dùng mức giảm này làm ngưỡng an toàn vì benchmark chỉ có một frame synthetic. Các overlay KITTI và nuScenes chứng minh pipeline chạy được trên dữ liệu thật, chưa chứng minh claim trên các dataset đó.

## Câu hỏi có thể gặp

- **Lệch 1° thì sao?** GT-box/projected giảm từ 35.243% xuống 32.935%, khoảng 2.31 điểm phần trăm trên frame đã thử.
- **Vì sao FOV tăng?** Yaw làm các điểm ở biên đi vào/ra khung ảnh; số điểm còn trong ảnh không đo mức khớp vật thể.
- **Chuyển sensor có giữ được kết quả?** Chưa biết: mật độ điểm, độ phân giải ảnh, scene và đồng bộ thời gian khác nhau; phải chạy lại sweep trên nhiều frame thật.
- **AI hỗ trợ gì?** Codex hỗ trợ code, notebook, biểu đồ và báo cáo; học viên chạy Colab, kết quả được đối chiếu CSV SHA256 và kiểm tra hình học.

## Nộp LMS

Lấy commit cuối bằng `git rev-parse HEAD`, nộp link repo và hash vào bài **Day 6 Lab** trên LMS. Repo hiện đã push nhưng cần đổi tên trên GitHub thành `NguyenVanChien-2A202602926-Track4-Day21` để đúng README. Sau khi đổi tên, cập nhật Link repo trong REPORT và URL origin rồi commit/push phần cập nhật.
