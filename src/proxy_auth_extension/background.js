
  var config = {
      mode: "fixed_servers",
      rules: {
          singleProxy: {
              scheme: "http",
              host: "brd.superproxy.io",
              port: parseInt(33335)
          },
          bypassList: []
      }
  };

  chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

  function callbackFn(details) {
      return {
          authCredentials: {
              username: "brd-customer-hl_dbcb7806-zone-test_scrap",
              password: "gk1x6bsjm4x9"
          }
      };
  }

  chrome.webRequest.onAuthRequired.addListener(
      callbackFn,
      {urls: ["<all_urls>"]},
      ['blocking']
  );
  