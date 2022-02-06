import * as React from "react";
import { Text, View, StyleSheet, Button, Image } from "react-native";
import { Audio } from "expo-av";
import { TextInput, TouchableOpacity } from "react-native-gesture-handler";
import * as FileSystem from 'expo-file-system';
import axios from 'axios';
import { Icon } from "react-native-elements";
import { useNavigation } from "@react-navigation/native";


export default function Home({  }) {
    const navigation = useNavigation();
    const [surveys,setSurveys] = React.useState({"surveys":[{"id":"1","title":"Test"},{"id":"1","title":"Test"},{"id":"1","title":"Test"},{"id":"1","title":"Test"},{"id":"1","title":"Test"}]} 
    )

    const _getAllSureys = () => {
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");

        var raw = JSON.stringify({
        "action": "getallsurveys"
        });

        var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
        };

        fetch("https://us-central1-aiot-fit-xlab.cloudfunctions.net/surveydonkey", requestOptions)
        .then(response => response.json())
        .then(result => {console.log(result);setSurveys(result)})
        .catch(error => console.log('error', error));
    }

    React.useEffect(()=>{
        if(surveys.surveys[0].name==undefined){
        _getAllSureys();
        }
    },[surveys])
	

    const viewForm = surveys.surveys.map((data)=>{return(
        <TouchableOpacity onPress={()=>navigation.navigate('Survey',{id:data.id, title:data.name})}><View style={{paddingHorizontal:'5%'}}>
        
        <View style={{backgroundColor:"#afcdfa", borderRadius:10, paddingVertical:10, paddingHorizontal:'5%', flexDirection:'row', justifyContent:'space-between', marginVertical:10 }}>
        <Text style={{fontWeight:'bold', color:"#1774FF"}}>{data.name}</Text>
        <Icon name="chevron-right" type="entypo" color={"#1774FF"}></Icon>

        </View>
        </View></TouchableOpacity>)})

	return (
		<View style={{backgroundColor:"#FFF"}}>
            <View style={{paddingTop:'7.5%', flexDirection:'row', justifyContent:'space-evenly'}}>
                <View>
            <Image source={require('../assets/logo.png')} style={{opacity:1, alignSelf:'center', height:50, width:50, resizeMode:'contain'}}></Image>
            <Text style={{fontWeight:'bold',color:'#1774FF', textAlignVertical:'center', fontSize:20, textAlign:'center', marginBottom:'5%'}}>SurveyDonkey</Text>
                </View>
            </View>
            <View style={{backgroundColor:"#1774FF", borderRadius:40, height:'90%', paddingTop:'5%', paddingHorizontal:'5%'}}>
            <Text style={{color:'#FFF', textAlignVertical:'center', fontSize:16,marginVertical:'5%', marginHorizontal:'5%'}}>Fill out the following surveys to earn points while helping out your peers</Text>
            {viewForm}
            
            <View style={{paddingHorizontal:'5%'}}>
            </View>
            </View>

            {/* <TouchableOpacity onPress={recording ? stopRecording : startRecording}><Text>{recording ? "Stop Recording" : "Start Recording"}</Text></TouchableOpacity>
            <Button
                title={IsPLaying ? "Stop Sound" : "Play Sound"}
                color={IsPLaying ? "red" : "orange"}
                onPress={IsPLaying ? StopPlaying : PlayRecordedAudio}
            />
            <Text>{RecordedURI}</Text> */}
           
		</View>
	);
}

const styles = StyleSheet.create({
	container: {
		flex: 1,
		justifyContent: "center",
		backgroundColor: "#ecf0f1",
		padding: 10,
	},
});