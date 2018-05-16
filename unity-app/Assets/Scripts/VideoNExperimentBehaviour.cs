using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class VideoNExperimentBehaviour : MonoBehaviour {
    public int serverPort = 40000;
    public GameObject screen;
    
    private TcpIpServer tcpServer;
    private UnityEngine.Video.VideoPlayer videoPlayer;
    private bool videoRemotePlay = false;
    private UnityEngine.Video.VideoClip videoClip;
    private int ixVideo = 0;

    private bool videoIsReady;
    private bool prepareVideo = false;
    private bool playVideo = false;

    // Use this for initialization
    void Start () 
    {
        Application.runInBackground = true;
        // Create TCP Server and Block until Client is connected
        tcpServer = new TcpIpServer("0.0.0.0", serverPort);
        // VideoPlayer component from Screen
        videoPlayer = screen.GetComponent<UnityEngine.Video.VideoPlayer>();
    }

    // Update is called once per frame
    void Update ()
    {
        if (this.tcpServer.IsDataAvailable())
        {
            ixVideo = this.tcpServer.ReadCommand();
            Debug.Log("Datum received: " + ixVideo.ToString());

            // Quit was requested
            if (ixVideo == 66)
            {
                Application.Quit();
            }
            // Video was requested
            else 
            {
                // Load video in Player
                videoPlayer.source = UnityEngine.Video.VideoSource.VideoClip;
                videoPlayer.clip = Resources.Load("video_" + ixVideo.ToString("D2")) as UnityEngine.Video.VideoClip;
                // Set AudioSource
                videoPlayer.audioOutputMode = UnityEngine.Video.VideoAudioOutputMode.AudioSource;
                videoPlayer.SetTargetAudioSource(0, screen.GetComponent<UnityEngine.AudioSource>());
                prepareVideo = true;
            }
        }

        // Video needs to be prepared
        if (prepareVideo)
        {
            videoPlayer.Prepare();
            prepareVideo = false; 
        }

        // Play the video if it's prepared  
        if (videoPlayer.isPrepared & !videoRemotePlay)
        {
            // Play Video
            videoPlayer.Play();
            // String ix_video
            Debug.Log("Playing video: " + ixVideo.ToString("D2"));
            // Set flag of remote play
            videoRemotePlay = true;
        }

        // Check that Video was remotely started and is over
        if (videoRemotePlay & !videoPlayer.isPlaying)
        {
            videoRemotePlay = false;
            tcpServer.WriteInt32(ixVideo);
            Debug.Log("End of video: " + ixVideo.ToString("D2"));
            videoPlayer.Stop();
        }      
    }
}
