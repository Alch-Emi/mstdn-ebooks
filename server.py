from flask import Flask

import main
import functions
import threading

application = Flask(__name__)
toot_cache = set()
currently_downloading = set()

@application.route("/@<handle>@<instance>")
def show_bot(instance, handle):
    accounts = main.client.account_search(f'{handle}@{instance}')
    if len(accounts):
        acc = accounts[0]
        if acc.id not in toot_cache:
            if acc.id not in currently_downloading:
                currently_downloading.add(acc.id)
                def download():
                    db, c = main.create_db('toots.db')
                    main.download_toots(acc, c)
                    db.commit()
                    db.execute("VACUUM") #compact db
                    db.commit()
                    db.close()
                    currently_downloading.remove(acc.id)
                    toot_cache.add(acc.id)
                threading.Thread(target=download).start()
                return f"Now downloading toots for {accounts[0].acct}"
            else:
                return f"Already downloading toots for {accounts[0].acct}"
        return functions.make_toot(user = acc.id)['toot']
    else:
        return "No account found"
