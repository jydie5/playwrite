from playwright.sync_api import Page
import logging
import time
import os
from pathlib import Path
from typing import Optional, Tuple

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OCCTOAuthenticator:
    """OCCTOの認証（証明書選択とログイン）を処理するクラス"""
    
    def __init__(self):
        self.user_id = os.getenv('OCCTO_ID_KEY')
        self.password = os.getenv('OCCTO_PW_KEY')
        
        if not self.user_id or not self.password:
            raise ValueError("環境変数 OCCTO_ID_KEY または OCCTO_PW_KEY が設定されていません")
        
        # 証明書選択ボタンの位置
        self.cert_positions = {
            "証明書選択ボタン": {"x": 448, "y": 332},
            "OKボタン": {"x": 866, "y": 441}
        }

    def click_cert_buttons(self):
        """証明書選択ダイアログのボタンをクリック"""
        import pyautogui
        
        # 証明書選択ボタンをクリック
        pos = self.cert_positions["証明書選択ボタン"]
        pyautogui.click(pos["x"], pos["y"])
        logger.info("証明書選択ボタンをクリックしました")
        time.sleep(1)

        # OKボタンをクリック
        pos = self.cert_positions["OKボタン"]
        pyautogui.click(pos["x"], pos["y"])
        logger.info("OKボタンをクリックしました")
        time.sleep(1)

    def handle_login(self, page: Page) -> bool:
        """ログインフォームの入力と送信"""
        try:
            # ユーザーIDの入力
            userid_field = page.locator('#userid')
            userid_field.fill(self.user_id)
            logger.info("ユーザーIDを入力しました")
            
            # パスワードの入力
            password_field = page.locator('#userpass')
            password_field.fill(self.password)
            logger.info("パスワードを入力しました")
            
            # 送信ボタンのクリック
            submit_button = page.locator('input[type="submit"][value="　送信　"]')
            submit_button.click()
            logger.info("送信ボタンをクリックしました")
            
            return True
            
        except Exception as e:
            logger.error(f"ログインフォームの処理でエラー: {e}")
            return False

    def authenticate(self, page: Page) -> bool:
        """認証プロセスを実行"""
        try:
            # メインページにアクセス
            logger.info("OCCTOメインページにアクセスしています...")
            try:
                page.goto(
                    "https://www.occto.or.jp/",
                    wait_until="commit",
                    timeout=10000
                )
                time.sleep(1)
            except Exception as e:
                logger.warning(f"メインページのロードでエラーが発生しましたが続行します: {e}")

            # ログインページへアクセス
            logger.info("ログインページにアクセスします...")
            try:
                page.goto(
                    "https://occtonet.occto.or.jp/members/dfw/SS/switch/top",
                    wait_until="commit",
                    timeout=3000
                )
            except Exception as e:
                logger.info("証明書選択ダイアログが表示されました")

            # 証明書選択ダイアログの処理
            time.sleep(1)
            self.click_cert_buttons()

            # ログインページの読み込みを待機
            try:
                page.wait_for_load_state("domcontentloaded", timeout=10000)
                page.wait_for_selector('#userid', timeout=10000)
                
                # ログインフォームの処理
                if self.handle_login(page):
                    logger.info("ログイン処理が完了しました")
                    page.wait_for_load_state("networkidle", timeout=30000)
                    return True
                else:
                    logger.error("ログイン処理に失敗しました")
                    return False
                
            except Exception as e:
                logger.error(f"ページ処理でエラー: {e}")
                return False

        except Exception as e:
            logger.error(f"認証プロセスでエラー: {e}")
            return False