import secsgem.gem
import code

class SampleEquipment(secsgem.gem.GemEquipmentHandler):
    def __init__(self, settings: secsgem.common.Settings):
        print(settings)
        super().__init__(settings)


def main():
    h = SampleEquipment("127.0.0.1", 5000, False, 0, "sampleequipment")
    h.enable()
    try:
        print('Server started')
        code.interact("equipment object is available as variable 'h', press ctrl-d to stop", local=locals())
    except KeyboardInterrupt:
        pass
    print('Stopping server...')
    h.disable()
        





if __name__ == '__main__':
    main()