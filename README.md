# Bitcoin-strategy-investment v1

### Mục tiêu
thì tui có đưa ra các mục tiêu như sau:
1. không cần suy nghĩ về việc đưa ra các quyết định mua hay bán, việc mua hay bán hoàn toàn phụ thuộc vào chương trình.
2. Đơn giản và dễ hiểu?
3. vốn thấp khả năng thực thi cao
4. tự động hóa nếu có.

Thì từ các lý thuyết và khái niệm cơ bản dễ hiểu trên, thì hiện tại tui đang suy nghĩ đến các từ khóa như, " giá - thời gian" , " dự đoán", " quy tắt", " cảnh báo" , "giả lập", "giao dịch" mọi ý tưởng hiện tại là mơ hồ nhưng tui đang suy nghĩ đến những từ khóa đó để thực thi cái chiến lược này giờ tôi mới bắt đầu triến khai các ý tưởng trên.

1. giá-thời gian : đối với giá thì tui coi nó như nguồn nước để tui khai thác là cơ sở đề tui đưa ra các quyết định về mua hay bán bitcoin. 
2. " dự đoán" : thì tui nghĩ tui sẽ không cố dự đoán giá  bitcoin làm gì mà thay vào đó là thực hiện việc  đưa ra các quy tắt về bitcoin để đầu tư thì tui sẽ nói ở phần sau:
3. "quy tắt" đây tui nghĩ là phần quan trọng nhất thi trong đầu tui hiện tại tồn tại một số khái niệm sơ sài về quy tắt mà mình phải tìm ra.

1. để tăng giá 10% thì bitcoin cần trung bình bao nhiêu thời gian?
2. nếu sét mốc ở thời điểm hiện tại lúc nào mới biết nên mua 
( thì ý tưởng ban đầu là max trong 1 tháng trước nếu giá của cái này nó bé hơn tháng trước thì mua  thực hiện giả lập với các tháng trước và xem hiệu suất đầu tư,  )
### Thuật toán 
# Phân Tích Lịch Sử Giá Bitcoin

## Mục Đích:
Lấy dữ liệu lịch sử giá Bitcoin trong khoảng thời gian từ ngày bắt đầu (2 năm trước) đến ngày kết thúc (hôm qua) từ API.

## Cách Thực Hiện:
Dữ liệu được lấy từ API `https://history.btc123.fans/api.php`, với các tham số:
- `symbol=bitcoin`
- `start= 2 năm trước'
- `end=  kết thúc hôm qua'

## Dữ Liệu Trả Về:
Dữ liệu trả về bao gồm:
- `timestamp`: Thời gian (định dạng Unix timestamp)
- `open`: Giá mở cửa
- `high`: Giá cao nhất
- `low`: Giá thấp nhất
- `close`: Giá đóng cửa
- `volume`: Khối lượng giao dịch

Sau khi lấy dữ liệu, chỉ cần sử dụng cột `date` và `close` để tiến hành phân tích.

## Tính Toán Xác Suất:

### Ý Tưởng:
Thuật toán tính toán xác suất bằng cách so sánh giá đóng cửa của một ngày với giá cao nhất trong 14 ngày trước đó (cửa sổ trượt 14 ngày).

### Quy Trình:
1. Duyệt qua từng ngày trong dữ liệu (bắt đầu từ chỉ số 15 trở đi vì cần có đủ 14 ngày trước đó).
2. Chọn một đoạn dữ liệu con có độ dài 14 ngày.
3. Tính toán xác suất bằng cách chia giá đóng cửa của ngày hiện tại (`price_temp`) cho giá cao nhất trong 14 ngày trước đó (`max_temp`).
4. Lưu kết quả xác suất vào bảng `prob`.

## Tính Toán Giá Trị X:

### Ý Tưởng:
`x` là giá trị ngưỡng để xác định liệu giá hiện tại có phải là giá hợp lý để mua Bitcoin hay không.

### Quy Trình:
1. Sắp xếp các giá trị xác suất (`probability`) theo thứ tự giảm dần.
2. Tính toán giá trị `x` là giá trị ở vị trí thứ 75% trong danh sách sắp xếp này. Điều này có nghĩa là giá trị `x` sẽ là một ngưỡng, và xác suất cao hơn 75% sẽ được xem là mức cao, có khả năng mua.

## Tính Toán `prob_yes` cho Ngày Hôm Qua:

### Ý Tưởng:
`prob_current` là xác suất cho thấy giá của Bitcoin trong ngày hôm qua so với giá cao nhất trong 14 ngày trước đó.

### Quy Trình:
1. Lấy giá của 14 ngày cuối cùng và tính toán giá cao nhất trong số đó.
2. Tính toán xác suất `prob_current` bằng cách chia giá của ngày hôm qua cho giá cao nhất trong 14 ngày trước đó.

## Khuyến Nghị:

### Ý Tưởng:
So sánh giá trị `prob_current` với giá trị `x`. Nếu `prob_current` nhỏ hơn `x`, khuyến nghị mua Bitcoin; nếu không, khuyến nghị không mua.

### Quy Trình:
1. Nếu `prob_current` nhỏ hơn `x`, tức là giá Bitcoin hôm nay có thể sẽ thấp hơn mức cao nhất trong 14 ngày qua và có thể tăng, khuyến nghị mua.
2. Nếu `prob_current` lớn hơn hoặc bằng `x`, tức là giá Bitcoin hôm nay không có dấu hiệu giảm mạnh, khuyến nghị không mua.

## Kết Luận:
Dựa trên phân tích trên, để đưa ra quyết định về việc có nên mua Bitcoin bằng USDT nếu đạt dưới threshold x  hay không, dựa vào các chỉ số xác suất và các ngưỡng tính toán được Sử dụng bullet API Key để xữ lí tự động thông báo khi đạt ngưỡng. .


