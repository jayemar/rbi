#!/usr/bin/env python

"""
Read characters from screen
"""
import logging
import threading
import time
import zmq

LOG_FILEPATH = '/var/log/rbi/'
PUBLISH_PORT = 5998
REPLY_PORT = 5999


class MessagingAgent(object):
    """ Object represeting a screen reader """
    def __init__(self, publish_port=PUBLISH_PORT, reply_port=REPLY_PORT):
        self.name = self.__class__.__name__
        print("Staring instance of class %s" % self.name)
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            filename=LOG_FILEPATH + self.name + '.log',
            filemode='a')
        logging.Formatter.converter = time.gmtime
        self._log = logging.getLogger(self.name)

        self.is_active = True

        self.ctx = zmq.Context()
        self.publish_port = publish_port
        self.reply_port = reply_port
        self._configure_messaging()
        self._log.info("ZMQ context created: %d, %d"
                       % (self.publish_port, self.reply_port))
        print("Publish port: %d\nReply port: %d"
              % (self.publish_port, self.reply_port))

    def __del__(self):
        """
        Release camera feed and close all OpenCV windows
        """
        self.publisher.close()
        self.ctx.destroy()
        print("%s shutdown" % self.name)

    def _configure_messaging(self):
        self._create_publisher()
        self.replier_thread = threading.Thread(
            target=self._create_replier)
        self.replier_thread.start()

    def _create_publisher(self):
        self.publisher = self.ctx.socket(zmq.PUB)
        self.publisher.bind('tcp://*:%s' % self.publish_port)
        self._log.debug("Listening on publisher socket")

    def _create_replier(self):
        self.replier = self.ctx.socket(zmq.REP)
        self.replier.bind('tcp://*:%s' % self.reply_port)
        self._log.debug("Listening on replier socket")
        poller = zmq.Poller()
        poller.register(self.replier, zmq.POLLIN)
        while self.is_active:
            try:
                socks = dict(poller.poll())
                if self.replier in socks and socks[self.replier] == zmq.POLLIN:
                    msg = self.replier.recv_pyobj()
                    self._log.debug("Received message: %s" % str(msg))
                    self._handle_request(msg)
            except KeyboardInterrupt:
                self.is_active = False
        self._log.info("Closing Reply socket")
        self.replier.close()

    def _handle_request(self, msg):
        """ Handle Requests """
        options = {'h or ?': "help; show these options",
                   'q': "quite/close agent"}
        if msg in ['h', '?']:
            self.replier.send_pyobj(options)
        if msg == 'q':
            self.is_active = False
            self.replier.send_pyobj("Command received to close Reader")
        else:
            self.replier.send_pyobj("Unknown command: %s" % msg)


if __name__ == '__main__':
    try:
        agent = MessagingAgent()
    except KeyboardInterrupt:
        print("Closing %s" % agent.name)
        agent.is_active = False
