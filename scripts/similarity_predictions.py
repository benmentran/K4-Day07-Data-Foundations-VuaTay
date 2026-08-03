"""
Similarity Predictions - Lab 7
Calculate cosine similarity for 5 pairs of sentences about E-commerce policies.
"""

import sys
sys.path.insert(0, '.')

from src.LuongBaoLong_2A202601682 import compute_similarity, MockEmbedder, LocalEmbedder

def get_embedder():
    """Try to use local embedder, fallback to mock."""
    try:
        return LocalEmbedder()
    except Exception as e:
        print(f"Local embedder not available: {e}")
        print("Using MockEmbedder for demonstration...")
        return MockEmbedder()

def main():
    print("=" * 60)
    print("Phần 4 - Dự đoán độ tương tự (Similarity Predictions)")
    print("=" * 60)

    # Chọn embedder
    embedder = get_embedder()
    print(f"Embedder: {embedder.__class__.__name__}\n")

    # 5 cặp câu về TMĐT
    pairs = [
        {
            "id": 1,
            "a": "Chính sách đổi trả hàng trong vòng 30 ngày kể từ ngày mua.",
            "b": "Quý khách có thể hoàn trả sản phẩm trong thời hạn 1 tháng kể từ khi nhận hàng.",
            "predicted": "cao",
            "reason": "Cả hai câu đều nói về chính sách đổi trả với thời hạn 30 ngày, cùng ngữ cảnh về quyền lợi khách hàng."
        },
        {
            "id": 2,
            "a": "Thanh toán bằng thẻ tín dụng Visa hoặc Mastercard được chấp nhận.",
            "b": "Các phương thức thanh toán được hỗ trợ gồm: thẻ ATM, thẻ visa, và ví điện tử MoMo.",
            "predicted": "cao",
            "reason": "Cả hai câu đều về phương thức thanh toán, có chung từ khóa 'thẻ', 'Visa'."
        },
        {
            "id": 3,
            "a": "Phí vận chuyển cho đơn hàng dưới 500.000đ là 25.000đ.",
            "b": "Cách nấu món phở bò truyền thống Việt Nam với nước dùng đậm đà.",
            "predicted": "thấp",
            "reason": "Câu A về phí ship, câu B về ẩm thực - hoàn toàn khác ngữ cảnh."
        },
        {
            "id": 4,
            "a": "Chính sách bảo mật thông tin khách hàng theo tiêu chuẩn quốc tế.",
            "b": "Chúng tôi cam kết bảo vệ dữ liệu cá nhân của bạn bằng mã hóa SSL 256-bit.",
            "predicted": "cao",
            "reason": "Cả hai đều về bảo mật và bảo vệ thông tin khách hàng."
        },
        {
            "id": 5,
            "a": "Thời gian giao hàng tiêu chuẩn là 3-5 ngày làm việc.",
            "b": "Đơn hàng sẽ được xử lý trong 24 giờ và giao trong khoảng 1 tuần.",
            "predicted": "cao",
            "reason": "Cả hai đều về thời gian giao hàng, cùng chủ đề vận chuyển."
        },
    ]

    results = []
    for pair in pairs:
        vec_a = embedder(pair["a"])
        vec_b = embedder(pair["b"])
        similarity = compute_similarity(vec_a, vec_b)

        # Xác định đúng/sai
        is_high = similarity > 0.5
        predicted_high = pair["predicted"] == "cao"
        correct = is_high == predicted_high

        results.append({
            "id": pair["id"],
            "a": pair["a"],
            "b": pair["b"],
            "predicted": pair["predicted"],
            "actual": "cao" if is_high else "thấp",
            "score": similarity,
            "correct": "✓" if correct else "✗",
            "reason": pair["reason"]
        })

        print(f"Cặp {pair['id']}:")
        print(f"  A: {pair['a'][:60]}...")
        print(f"  B: {pair['b'][:60]}...")
        print(f"  Dự đoán: {pair['predicted']}")
        print(f"  Thực tế: {similarity:.4f} ({'cao' if is_high else 'thấp'})")
        print(f"  Đúng: {'✓' if correct else '✗'}")
        print()

    # Tổng kết
    correct_count = sum(1 for r in results if r["correct"] == "✓")
    print("=" * 60)
    print(f"Tổng kết: {correct_count}/5 dự đoán đúng")
    print("=" * 60)

    # In markdown table
    print("\n--- Markdown Table cho báo cáo ---\n")
    print("| # | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |")
    print("|---|-------|-------|---------|--------------|-------|")
    for r in results:
        a_short = r['a'][:40] + "..." if len(r['a']) > 40 else r['a']
        b_short = r['b'][:40] + "..." if len(r['b']) > 40 else r['b']
        print(f"| {r['id']} | {a_short} | {b_short} | {r['predicted']} | {r['score']:.4f} | {r['correct']} |")

    # Tìm bất ngờ nhất
    print("\n--- Phân tích bất ngờ ---")
    for r in results:
        if r["correct"] == "✗":
            print(f"Cặp {r['id']} bất ngờ: {r['reason']}")

if __name__ == "__main__":
    main()
