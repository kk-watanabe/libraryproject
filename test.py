import os
import django
import threading
import time
from django.test import Client

# 1. Djangoの環境セットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryproject.settings')
django.setup()

from libraryapp.models import Book, Stock, User, Location # ※実際のモデル名やインポートパスに合わせて変更してください

def setup_test_data():
    """テスト用のデータをクリーンな状態で準備する関数"""
    print("🔧 テストデータの準備中...")
    
    # テスト用ユーザーの作成（いなければ作成）
    user_a, _ = User.objects.get_or_create(username="UserA")
    user_b, _ = User.objects.get_or_create(username="UserB")

    # 2. テスト用の配置場所（Location）を準備 👈 【追加】
    location, _ = Location.objects.get_or_create(name="テスト用書架")
    
    # 残り1冊の状況を作る
    book, _ = Book.objects.get_or_create(title="デバッグ用書籍（残り1冊）", isbn="9784000000000")
    
    # 一度関連する在庫をクリアして、確実に「残り1冊」にする
    Stock.objects.filter(book=book).delete()
    stock = Stock.objects.create(
        book=book,
        location=location,
        is_available=True
    ) # 貸出可能
    
    print(f"  ➜ 準備完了: {book.title} (在庫ID: {stock.id})")
    return user_a, user_b, book, stock

# 結果をスレッド間で共有するための辞書
results = {}

def send_borrow_request(user, book_id, stock_id, thread_name):
    """個々のユーザーとしてログインし、貸出ボタンをPOSTする関数"""
    client = Client()
    client.force_login(user) # 擬似的にログイン状態にする
    
    # 💥 同時タイミングを極限まで合わせるための待機
    time.sleep(0.5) 
    
    print(f"🚀 [{thread_name}] 貸出リクエスト送信！")
    
    # ※実際のURLパターン名やPOSTデータに合わせて書き換えてください
    # 例: /books/1/borrow/ へのリクエスト
    url = f"/books/{book_id}/borrow/" 
    data = {"stock_id": stock_id}
    
    # POSTリクエスト実行
    response = client.post(url, data, follow=True)
    
    # 結果を保存
    results[thread_name] = response

# --- メイン実行処理 ---
if __name__ == "__main__":
    print("==========================================")
    print("   ⚡ IT-13: 同時貸出（競合）テスト開始 ⚡   ")
    print("==========================================\n")
    
    user_a, user_b, book, stock = setup_test_data()
    
    # 2つのスレッド（擬似的なUserAとUserBの同時操作）を作成
    thread_a = threading.Thread(target=send_borrow_request, args=(user_a, book.id, stock.id, "UserA(先着想定)"))
    thread_b = threading.Thread(target=send_borrow_request, args=(user_b, book.id, stock.id, "UserB(僅差想定)"))
    
    print("\n[タイマー始動] 2つのリクエストを同時に放ちます...")
    # 同時スタート！
    thread_a.start()
    thread_b.start()
    
    # 両方のスレッドが終わるまで待つ
    thread_a.join()
    thread_b.join()
    
    print("\n==========================================")
    print("   📊 テスト結果の判定（エビデンス） 📊   ")
    print("==========================================")
    
    for user_name, res in results.items():
        print(f"\n👤 【{user_name}】の結果:")
        print(f"  ➜ 返ってきたステータスコード: {res.status_code}")
        
        # 500エラー（クラッシュ）していないかチェック
        if res.status_code == 500:
            print("  ❌ Fail: サーバー内部エラー(500)が発生し、システムがクラッシュしました。")
            continue
            
        # 画面に表示されたメッセージやHTMLの中身を確認
        content_str = res.content.decode('utf-8')
        
        if "直前に在庫切れとなりました" in content_str or "貸出中" in content_str:
            # 実際のビューが返すエラーメッセージ（コンテキスト）に合わせて調整してください
            print("  ✅ Pass: クラッシュせず、適切に在庫切れエラーを画面に返しています。")
        else:
            # メッセージの文言が含まれていないが、500エラーでもない場合
            print("  ➜ 画面コンテンツ（一部抜粋）:")
            print(f"    {content_str[:150]}...") 
            print("  ℹ️ 仕様通りのエラーメッセージが表示されているか目視で確認してください。")