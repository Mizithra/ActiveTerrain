import random



class WorldEvent:
    def __init__(self, name, function=None):
        self.name = name
        self.function = function

    def trigger(self):
        print(f"Event '{self.name}' triggered!")
        if self.function:
            self.function()

    def resolve(self):
        print(f"Event '{self.name}' resolved!")



def main():
    def sample_event_function():
        print("Sample event function executed!")

    event1 = WorldEvent("Sample Event", sample_event_function)
    event1.trigger()
    event1.resolve()

    for i in range(5):
        event = world_event_check()
        if event:
            event.trigger()


def world_event_check():
    # Placeholder for event checking logic
    if(random.random() < 0.1):  # 10% chance to trigger an event
        return WorldEvent("Random Event", lambda: print("A random event has occurred!"))

if __name__ == "__main__":
    main() 
