"""
Maze Explorer - Game mê cung với hệ thống thu thập sao và lưu điểm
Refactored để dễ bảo trì và mở rộng
"""

from core.engine import GameApp
from core.scene import SceneManager
from game.scenes import MenuScene

def main():
    """Khởi chạy game"""
    
    # Tạo game app
    game = GameApp()
    
    # Tạo scene manager với menu scene ban đầu
    scene_manager = SceneManager(MenuScene(game))
    game.set_scene_manager(scene_manager)
    
    # Chạy game
    game.run()

if __name__ == "__main__":
    main()
