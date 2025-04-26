from lightstreamer.client import SubscriptionListener


class SubListener(SubscriptionListener):
  def onItemUpdate(self, update):
    print("UPDATE " + update.getValue("stock_name") + " " + update.getValue("last_price"))