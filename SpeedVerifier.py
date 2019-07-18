from verifier import verifier
from SpeedProperty import SpeedProperty

class SpeedVerifier(verifier):

    def getValue(self):
        speedValue = SpeedProperty(self.componentForVerifier.resources).get()
        self.correntValue = speedValue


    def eval(self,):
        if self.correntValue == self.valueToCompare:
            return
        error = 'speed expected value: {} , but was: {}'.format(self.valueToCompare, self.correntValue)
        bdf = self.componentForVerifier.resources.conf_space_agent.getBdf()
        uscOrDsc = self.componentForVerifier.getUscOrDsc()
        self.eventHendler.addEvent(self.iter, error, bdf, uscOrDsc)