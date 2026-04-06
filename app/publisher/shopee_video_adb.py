import os
import time
import subprocess

class ShopeeVideoADB:
    """
    SIAA 2026 - Automação Shopee Video via ADB (Android Debug Bridge).
    Permite postagens em escala sem depender de APIs oficiais ou Captchas de Browser.
    """
    
    def __init__(self, device_id=None):
        self.device_id = device_id
        self.cmd_prefix = f"adb -s {device_id} " if device_id else "adb "
        
    def _run_cmd(self, cmd):
        full_cmd = self.cmd_prefix + cmd
        print(f"[ADB EXEC] {full_cmd}")
        return subprocess.run(full_cmd, shell=True, capture_output=True, text=True)

    def is_device_ready(self):
        res = self._run_cmd("devices")
        lines = res.stdout.strip().split('\n')
        return len(lines) > 1

    def push_video(self, local_path, remote_path="/sdcard/DCIM/SIAA_TEMP.mp4"):
        print(f"[ADB] Enviando vídeo para o dispositivo: {local_path} -> {remote_path}")
        self._run_cmd(f"push \"{local_path}\" {remote_path}")
        # Notifica a galeria do Android sobre o novo arquivo
        self._run_cmd(f"shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{remote_path}")
        return remote_path

    def open_shopee(self):
        print("[ADB] Abrindo App Shopee...")
        self._run_cmd("shell am start -n com.shopee.br/com.shopee.app.ui.home.HomeActivity")
        time.sleep(5)

    def tap(self, x, y):
        self._run_cmd(f"shell input tap {x} {y}")
        time.sleep(1.5)

    def type_text(self, text):
        # Substitui espaços por %s para o comando input text do ADB
        safe_text = text.replace(" ", "%s").replace("\n", "%s")
        self._run_cmd(f"shell input text \"{safe_text}\"")

    def publish_flow(self, video_path, caption, coords):
        """
        Executa o fluxo de postagem baseado em coordenadas pré-mapeadas.
        coords: dict com chaves 'btn_plus', 'btn_video', 'btn_gallery', 'btn_next', 'btn_publish'
        """
        if not self.is_device_ready():
            print("[ADB] ERRO: Nenhum dispositivo detectado!")
            return False

        # 1. Prepara o arquivo
        remote = self.push_video(video_path)
        
        # 2. Abre a Shopee
        self.open_shopee()
        
        # 3. Inicia fluxo de postagem (Exemplo de sequência hipotética)
        print("[ADB] Iniciando sequência de cliques...")
        self.tap(*coords['btn_plus'])      # Botão central +
        self.tap(*coords['btn_shopee_video']) # Opção Shopee Video
        self.tap(*coords['btn_gallery'])   # Abrir galeria
        self.tap(*coords['first_video'])   # Selecionar primeiro vídeo
        self.tap(*coords['btn_next'])      # Próximo / Continuar
        
        # 4. Legenda
        print(f"[ADB] Inserindo legenda: {caption[:20]}...")
        self.tap(*coords['field_caption'])
        self.type_text(caption)
        
        # 5. Publicar
        # self.tap(*coords['btn_publish'])
        print("[ADB] ✅ Fluxo concluído até a tela de finalização.")
        return True

if __name__ == "__main__":
    # Coordenadas de exemplo (devem ser calibradas pelo usuário de acordo com o celular)
    # Use 'adb shell uiautomator dump' para encontrar os elementos.
    COORDS_MOCK = {
        'btn_plus': (540, 2200),
        'btn_shopee_video': (800, 2000),
        'btn_gallery': (100, 2100),
        'first_video': (200, 400),
        'btn_next': (950, 2200),
        'field_caption': (300, 500),
        'btn_publish': (540, 2300)
    }
    
    bot = ShopeeVideoADB()
    if bot.is_device_ready():
        # bot.publish_flow("path/to/vid.mp4", "Oferta TOP #shopee", COORDS_MOCK)
        print("Dispositivo pronto para automação Shopee Video via ADB!")
    else:
        print("Conecte um dispositivo Android e ative o Debug USB.")
