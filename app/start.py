from playwright.sync_api import sync_playwright
from occto_auth import OCCTOAuthenticator
import logging
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # 認証クラスのインスタンス化
        authenticator = OCCTOAuthenticator()
        
        with sync_playwright() as p:
            logger.info("ブラウザを起動します...")
            browser = p.chromium.launch(
                channel='chrome',
                headless=False,
                args=[
                    '--ignore-certificate-errors',
                    '--window-size=1280,720'
                ]
            )

            context = browser.new_context(
                ignore_https_errors=True,
                viewport={'width': 1280, 'height': 720}
            )
            page = context.new_page()

            # 認証プロセスの実行
            if authenticator.authenticate(page):
                logger.info("認証が完了しました")
                # ここに認証後の処理を追加
            else:
                logger.error("認証に失敗しました")

            input("処理を終了するにはEnterを押してください...")
            browser.close()

    except Exception as e:
        logger.error(f"予期せぬエラー: {e}")
    except KeyboardInterrupt:
        logger.info("プログラムが中断されました")

if __name__ == "__main__":
    main()