# ================== SCENE SYSTEM ==================
class Scene:
    def __init__(self, game): 
        self.game = game
    
    def handle_event(self, e): 
        pass
    
    def update(self, dt): 
        pass
    
    def draw(self, screen): 
        pass

class SceneManager:
    def __init__(self, start_scene): 
        self.current = start_scene
    
    def switch(self, new_scene): 
        self.current = new_scene
    
    def handle_event(self, e): 
        self.current.handle_event(e)
    
    def update(self, dt): 
        self.current.update(dt)
    
    def draw(self, screen): 
        self.current.draw(screen)
