using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class GazeboUnitySync : MonoBehaviour
{
    [Header("Network Settings")]
    public string gazeboIpAddress = "127.0.0.1";
    public int gazeboPort = 8080;
    
    [Header("Robot Configuration")]
    public string robotId = "base_link";
    public Transform robotTransform;
    
    [Header("Sensors")]
    public GameObject lidarPointPrefab;
    private List<GameObject> lidarPoints = new List<GameObject>();
    
    private TcpClient tcpClient;
    private NetworkStream stream;
    private string receivedData = "";
    
    // Robot state variables
    private Vector3 targetPosition = Vector3.zero;
    private Quaternion targetRotation = Quaternion.identity;
    private bool hasNewState = false;
    
    // For thread safety
    private readonly object stateLock = new object();
    
    void Start()
    {
        robotTransform = this.transform; // Default to this game object if not set in inspector
        
        // Attempt to connect to Gazebo
        ConnectToGazebo();
        
        // Start coroutine to handle network data
        StartCoroutine(HandleNetworkData());
    }
    
    void ConnectToGazebo()
    {
        try
        {
            tcpClient = new TcpClient();
            tcpClient.Connect(gazeboIpAddress, gazeboPort);
            stream = tcpClient.GetStream();
            
            Debug.Log("Connected to Gazebo simulation");
        }
        catch (Exception e)
        {
            Debug.LogError("Failed to connect to Gazebo: " + e.Message);
        }
    }
    
    IEnumerator HandleNetworkData()
    {
        while (tcpClient != null && tcpClient.Connected)
        {
            if (stream.DataAvailable)
            {
                byte[] buffer = new byte[1024];
                int bytesRead = stream.Read(buffer, 0, buffer.Length);
                
                if (bytesRead > 0)
                {
                    string newData = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                    receivedData += newData;
                    
                    // Process complete JSON messages (assuming they're separated by newlines)
                    ProcessReceivedData();
                }
            }
            
            yield return new WaitForSeconds(0.01f); // Small delay to prevent excessive CPU usage
        }
        
        yield return null;
    }
    
    void ProcessReceivedData()
    {
        // Split by potential JSON separators
        string[] jsonMessages = receivedData.Split(new[] { '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries);
        
        for (int i = 0; i < jsonMessages.Length - 1; i++) // Process all but the last piece (may be incomplete)
        {
            if (jsonMessages[i].Trim().StartsWith("{") && jsonMessages[i].Trim().EndsWith("}"))
            {
                ProcessJsonMessage(jsonMessages[i].Trim());
            }
        }
        
        // Keep the last piece in case it's incomplete
        receivedData = jsonMessages[jsonMessages.Length - 1];
    }
    
    void ProcessJsonMessage(string json)
    {
        try
        {
            SimulationState state = JsonUtility.FromJson<SimulationState>(json);
            
            // Update robot state
            if (state.robots.ContainsKey(robotId))
            {
                RobotState robotState = state.robots[robotId];
                
                lock (stateLock)
                {
                    targetPosition = new Vector3(
                        robotState.position.x,
                        robotState.position.y,
                        robotState.position.z
                    );
                    
                    targetRotation = new Quaternion(
                        robotState.orientation.x,
                        robotState.orientation.y,
                        robotState.orientation.z,
                        robotState.orientation.w
                    );
                    
                    hasNewState = true;
                }
            }
            
            // Update sensor data
            UpdateSensorVisualization(state);
        }
        catch (Exception e)
        {
            Debug.LogError("Error processing JSON message: " + e.Message);
        }
    }
    
    void UpdateSensorVisualization(SimulationState state)
    {
        // Clear existing lidar points
        foreach (GameObject point in lidarPoints)
        {
            DestroyImmediate(point);
        }
        lidarPoints.Clear();
        
        // Display LiDAR data if available
        foreach (var sensorEntry in state.sensors)
        {
            if (sensorEntry.Value.type == "lidar")
            {
                LidarState lidarState = sensorEntry.Value;
                
                // Create visualization points for each range reading
                for (int i = 0; i < Mathf.Min(lidarState.ranges.Length, 100); i++) // Limit to 100 points to avoid performance issues
                {
                    if (lidarState.ranges[i] < lidarState.range_max && lidarState.ranges[i] > lidarState.range_min)
                    {
                        Vector3 pointPos = CalculateLidarPointPosition(i, lidarState.ranges[i], lidarState.angle_min, lidarState.angle_increment);
                        
                        GameObject point = Instantiate(lidarPointPrefab, transform.position + pointPos, Quaternion.identity);
                        point.transform.localScale = Vector3.one * 0.05f;
                        lidarPoints.Add(point);
                    }
                }
            }
        }
    }
    
    Vector3 CalculateLidarPointPosition(int index, float range, float angleMin, float angleIncrement)
    {
        float angle = angleMin + (index * angleIncrement);
        
        // Convert polar to Cartesian coordinates (in robot's local space)
        float x = range * Mathf.Cos(angle);
        float y = 0; // Typically lidar is horizontal
        float z = range * Mathf.Sin(angle);
        
        return new Vector3(x, y, z);
    }
    
    void Update()
    {
        // Smoothly interpolate to target position/rotation
        if (hasNewState)
        {
            lock (stateLock)
            {
                robotTransform.position = Vector3.Lerp(robotTransform.position, targetPosition, Time.deltaTime * 10f);
                robotTransform.rotation = Quaternion.Slerp(robotTransform.rotation, targetRotation, Time.deltaTime * 10f);
                
                hasNewState = false;
            }
        }
    }
    
    void OnDestroy()
    {
        if (stream != null)
            stream.Close();
        if (tcpClient != null)
            tcpClient.Close();
            
        // Clean up lidar visualization
        foreach (GameObject point in lidarPoints)
        {
            DestroyImmediate(point);
        }
    }
}

// Data classes to match the JSON structure from Python sync service
[System.Serializable]
public class SimulationState
{
    public float timestamp;
    public Dictionary<string, RobotState> robots;
    public Dictionary<string, object> environment; // Simplified
    public Dictionary<string, SensorState> sensors;
}

[System.Serializable]
public class RobotState
{
    public Position position;
    public Orientation orientation;
    public Velocity velocity;
    public double timestamp;
}

[System.Serializable]
public class Position
{
    public float x;
    public float y;
    public float z;
}

[System.Serializable]
public class Orientation
{
    public float x;
    public float y;
    public float z;
    public float w;
}

[System.Serializable]
public class Velocity
{
    public Linear linear;
    public Angular angular;
}

[System.Serializable]
public class Linear
{
    public float x;
    public float y;
    public float z;
}

[System.Serializable]
public class Angular
{
    public float x;
    public float y;
    public float z;
}

[System.Serializable]
public class SensorState
{
    public string type;
    public float[] ranges;
    public float[] intensities;
    public float angle_min;
    public float angle_max;
    public float angle_increment;
    public float range_min;
    public float range_max;
    public double timestamp;
}

[System.Serializable]
public class LidarState : SensorState
{
    // Inherits all fields from SensorState
}