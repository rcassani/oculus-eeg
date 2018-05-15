using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Demo : MonoBehaviour {
    public int serverPort = 40000;
    public GameObject screen;
    public GameObject hrText;
    public GameObject brText;
    public GameObject delta_bar;
    public GameObject theta_bar;
    public GameObject alpha_bar;
    public GameObject beta_bar;
    public GameObject gamma_bar;
    private TcpIpServer tcpServer;
    private UnityEngine.Video.VideoPlayer videoPlayer;
    private bool videoRemotePlay = false;
    private UnityEngine.Video.VideoClip videoClip;
    private int currentVideo = 0;
    private int requestVideo = 1;
    private int hrVal = 0;
    private int bkVal = 0;
    private int delta = 0;
    private int theta = 0;
    private int alpha = 0;
    private int betta = 0;
    private int gamma = 0;
    private Vector3 tmp_position;
    private Vector3 tmp_scale;




    private bool videoStarted;
    
    // Use this for initialization
    void Start () 
    {
        Application.runInBackground = true;
        // Create TCP Server and Block until Client is connected
        tcpServer = new TcpIpServer("0.0.0.0", serverPort);
        // VideoPlayer component from Screen
        videoPlayer = screen.GetComponent<UnityEngine.Video.VideoPlayer>();
        // Video index
        currentVideo = 0;
        requestVideo = 1;

    }

    // Update is called once per frame
    void Update ()
    {
        if (this.tcpServer.IsDataAvailable())
        {
            hrVal = this.tcpServer.ReadCommand();

            // given in blinks per second * 10000
            bkVal = this.tcpServer.ReadCommand();

            // power bands sum 10,000
            alpha = this.tcpServer.ReadCommand();
            betta = this.tcpServer.ReadCommand();
            delta = this.tcpServer.ReadCommand();
            theta = this.tcpServer.ReadCommand();
            gamma = this.tcpServer.ReadCommand();

            Debug.Log("HR received: " + hrVal.ToString());
            Debug.Log("BK received: " + bkVal.ToString());
            Debug.Log("D received: " + delta.ToString());
            Debug.Log("T received: " + theta.ToString());
            Debug.Log("A received: " + alpha.ToString());
            Debug.Log("B received: " + betta.ToString());
            Debug.Log("G received: " + gamma.ToString());


            // Update the UI HERE
            hrText.GetComponent<TextMesh>().text = "♥HR: " + hrVal.ToString() + " bpm";

            brText.GetComponent<TextMesh>().text = "⊖⊖BR: " + bkVal.ToString() + " bpm";


            tmp_scale = delta_bar.GetComponent<Transform>().localScale;
            tmp_scale.y = delta / 10000 * 2;
            delta_bar.GetComponent<Transform>().localScale = tmp_scale;
            tmp_position = delta_bar.GetComponent<Transform>().position;
            tmp_position.z = delta / 10000 * -1;
            delta_bar.GetComponent<Transform>().position = tmp_position;


            // Quit was requested, int(11)
            if (hrVal == 11)
            {
                Application.Quit();
            }
        }
        
        if(currentVideo != requestVideo)
        {
        // Load video in Player
        videoPlayer.source = UnityEngine.Video.VideoSource.VideoClip;
        videoPlayer.clip = Resources.Load("video_demo_" + requestVideo.ToString("D2")) as UnityEngine.Video.VideoClip;
        // Set AudioSource
        videoPlayer.audioOutputMode = UnityEngine.Video.VideoAudioOutputMode.AudioSource;
        videoPlayer.SetTargetAudioSource(0, screen.GetComponent<UnityEngine.AudioSource>());
        // Video needs to be prepared
        videoPlayer.Prepare();
        currentVideo = requestVideo;
        videoStarted = false;
        }

        // Play the video if it's prepared  
        if (videoPlayer.isPrepared & !videoStarted)
        {
            videoStarted = true;
            // Play Video
            videoPlayer.Play();
            // String ix_video
            Debug.Log("Playing video: " + currentVideo.ToString("D2"));    
        }

        // Check if Video is playing
        if (!videoPlayer.isPlaying & videoStarted)
        {
            //request new video
            Debug.Log("End of video: " + currentVideo.ToString("D2"));
            videoPlayer.Stop();
            requestVideo = currentVideo + 1;
            if(requestVideo > 6)
            {
                requestVideo = 1;
            }
        }      
    }
}
