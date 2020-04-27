from Object import Object


class InteractionType:
    MENU = 0


class InteractiveObject:
    def __init__(self):
        self.interacting = False
        self.interacting_type = InteractionType.MENU
        pass

    def interacting_behaviour(self, events):
        pass

    def custom_interacting_draw(self, surface):
        pass
