"""Run similarity predictions with UTF-8 output to file."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from src.LuongBaoLong_2A202601682 import compute_similarity, MockEmbedder, LocalEmbedder


def get_embedder():
    try:
        return LocalEmbedder()
    except Exception as e:
        print(f"Local embedder not available: {e}", flush=True)
        print("Using MockEmbedder...", flush=True)
        return MockEmbedder()


def main():
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append("Phan 4 - Du doan do tuong tu (Similarity Predictions)")
    output_lines.append("=" * 60)
    embedder = get_embedder()
    output_lines.append(f"Embedder: {embedder.__class__.__name__}")
    output_lines.append("")

    pairs = [
        {
            "id": 1,
            "a": "Chinh sach doi tra hang trong vong 30 ngay ke tu ngay mua.",
            "b": "Quy khach co the hoan tra san pham trong thoi han 1 thang ke tu khi nhan hang.",
            "predicted": "cao",
            "reason": "Cung noi ve doi tra thoi han 30 ngay",
        },
        {
            "id": 2,
            "a": "Thanh toan bang the tin dung Visa hoac Mastercard duoc chap nhan.",
            "b": "Cac phuong thuc thanh toan duoc ho tro gom: the ATM, the visa, va vi dien tu MoMo.",
            "predicted": "cao",
            "reason": "Cung noi ve phuong thuc thanh toan",
        },
        {
            "id": 3,
            "a": "Phi van chuyen cho don hang duoi 500.000d la 25.000d.",
            "b": "Cach nau mon pho bo truyen thong Viet Nam voi nuoc dung dam da.",
            "predicted": "thap",
            "reason": "Phi ship vs am thuc - khac ngu canh",
        },
        {
            "id": 4,
            "a": "Chinh sach bao mat thong tin khach hang theo tieu chuan quoc te.",
            "b": "Chung toi cam ket bao ve du lieu ca nhan cua ban bang ma hoa SSL 256-bit.",
            "predicted": "cao",
            "reason": "Cung noi ve bao mat va bao ve thong tin",
        },
        {
            "id": 5,
            "a": "Thoi gian giao hang tieu chuan la 3-5 ngay lam viec.",
            "b": "Don hang se duoc xu ly trong 24 gio va giao trong khoang 1 tuan.",
            "predicted": "cao",
            "reason": "Cung noi ve thoi gian giao hang",
        },
    ]

    results = []
    for pair in pairs:
        vec_a = embedder(pair["a"])
        vec_b = embedder(pair["b"])
        similarity = compute_similarity(vec_a, vec_b)
        is_high = similarity > 0.5
        predicted_high = pair["predicted"] == "cao"
        correct = is_high == predicted_high

        results.append({
            "id": pair["id"],
            "a": pair["a"],
            "b": pair["b"],
            "predicted": pair["predicted"],
            "actual": "cao" if is_high else "thap",
            "score": similarity,
            "correct": "Y" if correct else "N",
            "reason": pair["reason"],
        })

        output_lines.append(f"Cap {pair['id']}:")
        output_lines.append(f"  A: {pair['a']}")
        output_lines.append(f"  B: {pair['b']}")
        output_lines.append(f"  Du doan: {pair['predicted']}")
        output_lines.append(f"  Thuc te: {similarity:.4f} ({'cao' if is_high else 'thap'})")
        output_lines.append(f"  Dung: {'Y' if correct else 'N'}")
        output_lines.append("")

    correct_count = sum(1 for r in results if r["correct"] == "Y")
    output_lines.append("=" * 60)
    output_lines.append(f"Tong ket: {correct_count}/5 du doan dung")
    output_lines.append("=" * 60)

    # Write to file
    with open("scripts/similarity_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    # Also print to console (ASCII safe)
    print("Done. Results written to scripts/similarity_results.txt")
    print(f"\nFinal results:")
    for r in results:
        print(f"  Pair {r['id']}: predicted={r['predicted']}, actual={r['actual']}, score={r['score']:.4f}, correct={r['correct']}")
    print(f"Total: {correct_count}/5 correct")


if __name__ == "__main__":
    main()
