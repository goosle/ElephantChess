import torch 
import torch.nn.functional as TNF
import torch.nn.optimizer as TNO
import numpy

INPUT_LAYER = 21
BOARD_WIDTH = 9
BOARD_HEIGHT = 10
BOARD_AREA  =BOARD_WIDTH * BOARD_HEIGHT
ACTION_PROB = 187
VALUE_LOSS = 1
class Net(torch.nn.Module):
    ''' net module '''
    def __init__(self):
        super(Net, self).__init__()
        '''
    boards :
         n,21,10,9
    calculate methods:
         1: 3 conv 64=>128=>256
         2: action probobility:conv(4)  ,fc(4*10*9) =>fc(187) 
         3: state value:conv(2) ,fc(2*10*9)=> fc(64)=>fc(1) 
        '''
        #batch normal
        self.BN = torch.nn.BatchNorm2d(2,affine=True)
        #conv layer
        self.conv1 = torch.nn.Conv2d(INPUT_LAYER,64,kernel_size= 3,padding=1)
        self.conv2 = torch.nn.Conv2d(64,128,kernel_size= 3,padding=1)
        self.conv3 = torch.nn.Conv2d(128,256,kernel_size= 3,padding=1)
        #action probility
        self.actConv1 = torch.nn.Conv2d(256,4,kernel_size= 1)
        self.actProb = torch.nn.Linear(4*BOARD_AREA,ACTION_PROB)
        #state value
        self.svConv1 = torch.nn.Conv2d(256,2,kernel_size=1)
        self.svFC1 = torch.nn.Linear(2*BOARD_AREA,64)
        self.stateValue = torch.nn.Linear(64,1)
        pass
    

    def forward(self,boards):
        conv1 = TNF.relu(self.conv1(boards))
        conv2 = TNF.relu(self.conv2(conv1))
        conv3 = TNF.relu(self.conv3(conv2))
        
        actConv1 = TNF.relu(self.actConv1(conv3))
        bActConv1 = self.BN(actConv1)
        bActConv1Flat = bActConv1.view(-1,4*BOARD_AREA,ACTION_PROB) 
        actProb = TNF.softmax(self.actProb(bActConv1Flat))
        
        svConv1 = TNF.relu(self.svConv1(conv3))
        bsvConv1 = self.BN(svConv1)
        svConv1Flat = bsvConv1.view(-1,2*BOARD_AREA,64)
        svFC1 =   TNF.sigmoid(self.svFC1(svConv1Flat))
        stateValue = TNF.tanh(self.stateValue(svFC1))# state value range(-1,1) -1 lose,0 tie,1 win
        return actProb ,stateValue


 class PoliceValueNet():
    ''' police-value network''' 
    def __init__(self,modelFile = None):
        self.net = self.Net()

        self.l2_const = 1e-4
        self.optimizer =   TNO.Adam(self.net.parameters(),weight_deday= self.l2_const)

        if modelFile: 
            netParams = torch.load(medlFile)
            self.net.load_state_dict(netParams)

    def batchPolices(self,stateBatch):
        stateBatch = Vaiable(torch.FloatTensor(stateBatch).cuda())
        actProbs,value = self.net(stateBatch)
        return  actProbs.data.cpu().numpy(),value.data.cpu().numpy
  
    def policeValue(self,board):
        legalPos = board.availables  
        currentState = np.ascontiguousarray(board.cuurentState().reshape(-1,))
        actProbs,value = self.net(Variable(torch.from_numpy(currentState))).cuda().float())
        actProbs = actProbs.data.cpu().numpy().faltten()
        value = value.data[0][0]
        return zip(legalPos,actProbs)
        
    def trainStep(self,state_batch, mcts_probs, winner_batch,,lr):
        stateBatch = Variable(torch.FloatTensor(state_batch).cuda())
        actProbs = Variable(torch.FloatTensor(mcts_probs).cuda())
        winners = Variable(torch.FloatTensor(winner_batch).cuda())
        
        preActs , values = self.net(stateBatch)

        self.optimizer.zero_grad()
        """Sets the learning rate to the given value"""
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr
        
        valueLoss = TNF.mse_loss(values.view(-1),winners)
        policyLoss = TNF.nll_loss(np.log(preActs))
        policyLoss1 = -torch.mean(
                torch.sum(mcts_probs * np.log(preActs), 1)
                ) 
        print('policyLoss ',policyLoss,policyLoss1)
        loss = valueLoss + policyLoss     
        loss.backward()    
        self.optimizer.step()
              # calc policy entropy, for monitoring only
        entropy = -torch.mean(
                torch.sum(preActs * np.log(preActs), 1)
                )  
        return loss,entropy 
    pass



if  __name__ == "__main__":
    net = CNNet()
    print(net)
