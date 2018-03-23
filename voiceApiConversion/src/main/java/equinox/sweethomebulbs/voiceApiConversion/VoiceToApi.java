package equinox.sweethomebulbs.voiceApiConversion;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.support.v4.content.ContextCompat;
import android.util.Log;
import android.view.View;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import ai.api.AIListener;
import ai.api.android.AIConfiguration;
import ai.api.android.AIService;
import ai.api.model.AIError;
import ai.api.model.AIOutputContext;
import ai.api.model.AIResponse;
import ai.api.model.ResponseMessage;
import ai.api.model.Result;
import cz.msebera.android.httpclient.client.HttpClient;
import cz.msebera.android.httpclient.client.methods.HttpPost;
import cz.msebera.android.httpclient.entity.StringEntity;
import cz.msebera.android.httpclient.impl.client.DefaultHttpClient;
import cz.msebera.android.httpclient.message.BasicHeader;
import cz.msebera.android.httpclient.protocol.HTTP;

import com.google.gson.JsonElement;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.Iterator;
import java.util.List;
import java.util.Map;

public class VoiceToApi extends AppCompatActivity implements AIListener {

    private TextView inputQueryTv;
    private TextView intentTv;
    private TextView outputTv;
    private TextView promptTv;

    private ImageButton mSpeakBtn;

    private AIService aiService;

    JSONObject json = new JSONObject();

    final AIConfiguration config = new AIConfiguration("1d61e2d21a264a68ad9a29494c7b39c0",
            AIConfiguration.SupportedLanguages.Spanish,
            AIConfiguration.RecognitionEngine.System);


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.content_voice_to_api);

        aiService = AIService.getService(this, config);
        aiService.setListener((AIListener) this);

        inputQueryTv = findViewById(R.id.inputQuery);
        intentTv = findViewById(R.id.intent);
        outputTv = findViewById(R.id.output);

        mSpeakBtn = (ImageButton) findViewById(R.id.btnSpeak);
        mSpeakBtn.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(final View view) {
                requestAudioPermissions();
            }
        });
    }

    @Override
    public void onResult(final AIResponse response) {
        Result result = response.getResult();

        json = new JSONObject();
        try {
            json.put("action", response.getResult().getAction());
            JSONObject parameters = new JSONObject();
            for (final Map.Entry<String, JsonElement> entry : result.getParameters().entrySet()) {
                parameters.put(entry.getKey(), entry.getValue());
            }
            json.put("parameters", parameters);
            JSONArray contexts = new JSONArray();
            for (AIOutputContext context : result.getContexts()) {
                JSONObject cont = new JSONObject();
                cont.put("name", context.getName());
                JSONObject param = new JSONObject();
                for (final Map.Entry<String, JsonElement> entry : context.getParameters().entrySet()) {
                    if (!entry.getKey().contains("original")){
                        param.put(entry.getKey(), entry.getValue());
                    }
                }
                cont.put("parameters", param);
                cont.put("lifespan", context.getLifespan());
                contexts.put(cont);
            }
            json.put("contexts", contexts);
            json.put("actionIncomplete", result.isActionIncomplete());
        } catch (JSONException e) {
            e.printStackTrace();
        }

        Log.d("json", json.toString());

        String speech = result.getFulfillment().getSpeech();

        inputQueryTv.setText(result.getResolvedQuery());
        intentTv.setText(result.getAction());
        outputTv.setText("> " + speech);
        new SendToBicho().execute(json.toString());
    }


    @Override
    public void onError(final AIError error) {
        outputTv.setText("Bicho bombilla no te ha entendido :(");
    }

    @Override
    public void onListeningStarted() {
        mSpeakBtn.setImageResource(R.drawable.ic_sync_black);
    }

    @Override
    public void onListeningCanceled() {
        mSpeakBtn.setImageResource(R.drawable.ic_mic_black_100);
    }

    @Override
    public void onListeningFinished() {
        mSpeakBtn.setImageResource(R.drawable.ic_mic_black_100);
    }

    @Override
    public void onAudioLevel(final float level) {
    }

    //Requesting run-time permissions

    //Create placeholder for user's consent to record_audio permission.
    //This will be used in handling callback
    private final int MY_PERMISSIONS_RECORD_AUDIO = 1;

    private void requestAudioPermissions() {
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.RECORD_AUDIO)
                != PackageManager.PERMISSION_GRANTED) {

            //When permission is not granted by user, show them message why this permission is needed.
            if (ActivityCompat.shouldShowRequestPermissionRationale(this,
                    Manifest.permission.RECORD_AUDIO)) {
                Toast.makeText(this, "Please grant permissions to record audio", Toast.LENGTH_LONG).show();

                //Give user option to still opt-in the permissions
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.RECORD_AUDIO},
                        MY_PERMISSIONS_RECORD_AUDIO);

            } else {
                // Show user dialog to grant permission to record audio
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.RECORD_AUDIO},
                        MY_PERMISSIONS_RECORD_AUDIO);
            }
        }
        //If permission is granted, then go ahead recording audio
        else if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.RECORD_AUDIO)
                == PackageManager.PERMISSION_GRANTED) {

            //Go ahead with recording audio now
            aiService.startListening();
        }
    }

    //Handling callback
    @Override
    public void onRequestPermissionsResult(int requestCode,
                                           String permissions[], int[] grantResults) {
        switch (requestCode) {
            case MY_PERMISSIONS_RECORD_AUDIO: {
                if (grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    // permission was granted, yay!
                    aiService.startListening();
                } else {
                    // permission denied, boo! Disable the
                    // functionality that depends on this permission.
                    Toast.makeText(this, "Permissions Denied to record audio", Toast.LENGTH_LONG).show();
                }
                return;
            }
        }
    }

    @Override
    public void onDestroy() {
        super.onDestroy();

        if (aiService != null) {
            aiService.cancel();
        }
    }

}