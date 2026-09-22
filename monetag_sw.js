/*
 RacharlaGPT Monetag service-worker reference.
 Deploy at the site's root only if this exact zone is still active in the Monetag dashboard.
 Do not combine this with a different Monetag service-worker zone without checking the dashboard.
*/
self.options = {
    "domain": "5gvci.com",
    "zoneId": 11852352
}
self.lary = ""
importScripts('https://5gvci.com/act/files/service-worker.min.js?r=sw')
