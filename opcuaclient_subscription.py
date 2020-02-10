#########################################################################################################################
# Name: opc ua client
# Version: 0.1

# Activities:                                           Author:                         Date:
# Initial comment                                       RK                              20190409
# Add toggle module                                     RK                              20190411
# Add computer name to the client                       RK                              20190411
# Changed order to subscribe/ publish                   RK                              20190411
# Moved the try statement inside the for loop           RK                              20190425
# Changed from time to datetime to show milliseconds    RK                              20190508

########################################################################################################################
from opcua import Client
from opcua import ua
from opcua.common import ua_utils
import pandas as pd
import datetime
import logging
import socket

# toggle function
def toggle():
    if datetime.datetime.now().second % 10 < 5:
        toggle = False
    else:
        toggle = True
    return toggle

# Definition action if you receive read variable
class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing. You have to define here
    what to do with the received date.
    """

    def __init__(self):
        self.df_Read = pd.DataFrame(data={'node': [], 'node': [], 'value': []}).astype('object')

    def datachange_notification(self, node, val, data):
        try:
            df_New = pd.DataFrame(data={'timestamp': [], 'node': [], 'value': []}).astype('object')
            df_New.at[0, 'timestamp'] = datetime.datetime.now().replace(microsecond=0)
            df_New.at[0, 'node'] = str(node)[18:-2]
            df_New.at[0, 'value'] = float(val)
            self.df_Read= pd.concat([self.df_Read, df_New], axis=0)
            self.df_Read.where(self.df_Read['timestamp'] >= datetime.datetime.now() - pd.to_timedelta(1, unit='h'), inplace=True)
            self.df_Read.dropna(inplace=True)
            self.df_Read.drop_duplicates(subset=['timestamp', 'node'], inplace=True, keep='last')
            logging.info('%s read\t %s %s'%(datetime.datetime.now(),node,val))
            #print('%s read\t %s %s'%(datetime.datetime.now(),node,val))
            return self.df_Read
        except Exception as e:
            print(e)


    def event_notification(self, event):
        print("Python: New event", event)


# Definition of opcua client
class opcua(object):
    def __init__(self,  url= 'opc.tcp://ehub.nestcollaboration.ch:49320',
                        application_uri= 'Researchclient',
                        product_uri= 'Researchclient',
                        user= 'JustforTest',
                        password= 'JustforTest'):



        # Configuration client
        self.client = Client(url=url, timeout=4) # You have to enter the url of the opc ua server e.g "opc.tcp://ehub.nestcollaboration.ch:49320"
        self.client.set_user(user)  # You have to enter your User name*
        self.client.set_password(password)  # You have to enter your password*
        self.client.application_uri= application_uri + ":" + socket.gethostname()+":" + user# You have to enter the uri according to the name or path of your certificate and key*
        self.client.product_uri =product_uri + ":" + socket.gethostname() + ":" + user# You have to enter the uri according to the name or path of your certificate and key*
        ##self.self.client.set_security_string("Basic128Rsa15,SignAndEncrypt,uaexpert.der,uaexpert_key.pem")  # You have to enter the name or path of your certificate and key*
        self.df_Write = pd.DataFrame({'node': [], 'value': []})
        self.handler = SubHandler()



    def connect(self):
        # Connect to server
        try:
            self.client.connect()
            self.client.load_type_definitions()  # load definition of server specific structures/extension objects
            print('%s OPC UA Connection to server established' % datetime.datetime.now())
        except:
            self.client.disconnect()
            print('%s OPC UA Connection to server could not be established' % datetime.datetime.now())

    def disconnect(self):
        self.client.disconnect()
        print('%s OPC UA Server disconnected' % datetime.datetime.now())


    def subscribe(self, df_Read=pd.DataFrame({'node': ['ns=2;s=Gateway.PLC1.65NT-06402-D001.PLC1.microgrid.strRead.strBatterienSystem.bAckResearch']})):
            # subscribing to a variable node (read)
            # Configure nodes to read
            nodelistRead = []
            for index, row in df_Read.iterrows():
                nodelistRead.append(self.client.get_node(row['node']))

            try:
                handler = self.handler
                sub = self.client.create_subscription(period=0, handler=handler)
                sub.subscribe_data_change(nodelistRead)
                # print('%s OPC UA Subscription requested' % datetime.datetime.now())
            except Exception as e: print(e)

    def publish(self,df_Write= pd.DataFrame({  'node':["ns=2;s=Gateway.PLC1.65NT-06402-D001.PLC1.microgrid.strRead.strBatterienSystem.bAckResearch"],'value':[True]})):
        # find out datatype of write nodes
        # df_ToSend = pd.concat([self.df_Write,df_Write],ignore_index= True) # concatanate the df of the last time step and the actual time step
        # df_ToSend.drop_duplicates(subset=['node', 'value'], inplace=True, keep=False) #drop all rows which didnt change
        # df_ToSend.drop_duplicates(subset=['node'], inplace=True, keep='first') #drop the old value of the rows that changed
        # self.df_Write = df_Write # copy the actual df to the old df
        for index, row in df_Write.iterrows():
            try:
                node = self.client.get_node(row.node)
                datatype= node.get_data_type_as_variant_type()
                value = ua_utils.string_to_val(str(row.value),datatype)
                node.set_value(ua.DataValue(ua.Variant(value,datatype)))
                logging.info('%s write %s %s' % (datetime.datetime.now(), node, value))
                # print('%s write %s %s' % (datetime.datetime.now(), node, value))

            except Exception as e:
                print(e)
