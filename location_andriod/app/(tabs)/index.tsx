import React, { useState } from 'react';
import { StyleSheet, Text, View, Button } from 'react-native';
import * as Location from 'expo-location';

export default function App() {
  const [location, setLocation] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const getLocation = async () => {
    let { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      setErrorMsg('Permission to access location was denied');
      return;
    }

    let currentLocation = await Location.getCurrentPositionAsync({});
    console.log('new location: ',currentLocation)
    setLocation(currentLocation);
    
    sendLocationData(currentLocation.coords.latitude, currentLocation.coords.longitude)
    console.log('location sent: ',currentLocation)
  };

  const sendLocationData = async (latitude, longitude) => {
    try {
      const response = await fetch('http://192.168.43.145:8000/location/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ latitude, longitude }),
      });

      if (!response.ok) {
        throw new Error('Failed to send location data');
      }

      console.log('Location data sent successfully');
    } catch (error) {
      console.error('Error:', error);
    }
  };



  return (
    <View style={styles.container}>
      <Text>Location:</Text>
      {errorMsg && <Text style={styles.errorMsg}>{errorMsg}</Text>}
      {location && (
        <Text>
          Latitude: {location.coords.latitude}, Longitude: {location.coords.longitude}
        </Text>
      )}
      <Button title="Get Location" onPress={getLocation} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  errorMsg: {
    color: 'red',
  },
});
