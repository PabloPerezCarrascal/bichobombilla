package equinox.sweethomebulbs.voiceApiConversion;


import android.os.AsyncTask;

import cz.msebera.android.httpclient.client.HttpClient;
import cz.msebera.android.httpclient.client.methods.HttpPost;
import cz.msebera.android.httpclient.entity.StringEntity;
import cz.msebera.android.httpclient.impl.client.DefaultHttpClient;
import cz.msebera.android.httpclient.message.BasicHeader;
import cz.msebera.android.httpclient.protocol.HTTP;

public class SendToBicho extends AsyncTask<String, Void, Void> {

    protected Void doInBackground(String... content) {
        // Create a new HttpClient and Post Header
        HttpClient httpclient = new DefaultHttpClient();
        HttpPost httppost = new HttpPost("http://aurum.hi.inet:55111/bichobombilla/");

        try {
            StringEntity se = new StringEntity(content[0]);
            se.setContentType(new BasicHeader(HTTP.CONTENT_TYPE, "application/json"));
            httppost.setEntity(se);
            httpclient.execute(httppost);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

}
