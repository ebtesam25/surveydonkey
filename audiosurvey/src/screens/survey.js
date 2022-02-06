import * as React from "react";
import { Text, View, StyleSheet, Button, Image } from "react-native";
import { Audio } from "expo-av";
import { TextInput, TouchableOpacity } from "react-native-gesture-handler";
import * as FileSystem from 'expo-file-system';
import axios from 'axios';
import { Icon } from "react-native-elements";
import { useNavigation } from "@react-navigation/native";


export default function Survey({ route }) {
    const navigation = useNavigation();
    const { id , title } = route.params;
	const [recording, setRecording] = React.useState(false);
    const [sound, setSound] = React.useState();
    const [tax, setTx] = React.useState({})
    const [answers, setAnswers] = React.useState([]);
    const [status, setStatus] = React.useState("")
    const AudioPlayer = React.useRef(new Audio.Sound());
    const [count, setCount] = React.useState(0);
    const [points, setPoints] = React.useState(0);
    const [values, setValues] = React.useState([]);

  // States for UI
  const [RecordedURI, SetRecordedURI] = React.useState("");
  const [AudioPermission, SetAudioPermission] = React.useState(false);
  const [IsRecording, SetIsRecording] = React.useState(false);
  const [IsPLaying, SetIsPLaying] = React.useState(false);
  const [questions,setQuestions] = React.useState({"default":true,"questions":[{'id':'1','text':'Whats your name?'},{'id':'1','text':'Whats your name?'},{'id':'1','text':'Whats your name?'},{'id':'1','text':'Whats your name?'},{'id':'1','text':'Whats your name?'},{'id':'1','text':'Whats your name?'},{'id':'1','text':'Whats your name?'}]})

  const _getSurvey = () => {
    var myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    
    var raw = JSON.stringify({
      "action": "getsurveybyid",
      "surveyid": id
    });
    
    var requestOptions = {
      method: 'POST',
      headers: myHeaders,
      body: raw,
      redirect: 'follow'
    };
    
    fetch("https://us-central1-aiot-fit-xlab.cloudfunctions.net/surveydonkey", requestOptions)
      .then(response => response.json())
      .then(result => {console.log(result); setQuestions(result);
        var i =0;
        for(i=0;i<result.questions.length;i++){
            setAnswers(...answers,' ');
        }

    })
      .catch(error => console.log('error', error));
  }
  async function playSound(file) {
    console.log('Loading Sound');
    const { sound } = await Audio.Sound.createAsync(
       file
    );
    setSound(sound);

    console.log('Playing Sound');
    await sound.playAsync(); }

  React.useEffect(() => {
      if(questions.default){
      _getSurvey();
      }
    return sound
      ? () => {
          console.log('Unloading Sound');
          sound.unloadAsync(); }
      : undefined;
  }, [sound]);

	async function startRecording() {
		console.log("hey");
		try {
			console.log("Requesting permissions..");
			await Audio.requestPermissionsAsync();
			await Audio.setAudioModeAsync({
				allowsRecordingIOS: true,
				playsInSilentModeIOS: true,
			});
			console.log("Starting recording..");
			const { recording } = await Audio.Recording.createAsync({
				android: {
					extension: ".wav",
					audioEncoder: Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY,
					sampleRate: 44100,
					numberOfChannels: 1,
					bitRate: 128000,
				},
				ios: {
					extension: ".mp4",
					outputFormat: Audio.RECORDING_OPTION_IOS_OUTPUT_FORMAT_MPEG4AAC,
					audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_MAX,
					sampleRate: 44100,
					numberOfChannels: 2,
					bitRate: 128000,
					linearPCMBitDepth: 16,
					linearPCMIsBigEndian: false,
					linearPCMIsFloat: false,
				},
			});
			setRecording(recording);
			console.log("Recording started");
		} catch (err) {
			console.error("Failed to start recording", err);
		}
	}
    const _publish = (data, uri) =>{   
        let cloudinary = 'https://api.cloudinary.com/v1_1/diywehkap/image/upload';
         console.log(data)
         var fd = new FormData();
         let audio64 = `data:audio/x-wav;base64,${data}`

        fd.append("file", audio64 );

        fd.append("upload_preset", "hm4fkyir");
        fd.append("resource_type", "raw")

        fetch('https://api.cloudinary.com/v1_1/diywehkap/upload',
        {
            method: 'POST',
            body: fd
        }
        ).then(async r => {
           let data = await r.json()
           let curl=data.secure_url;
           
        //    const assembly = axios.create({
        //     baseURL: "https://api.assemblyai.com/v2",
        //     headers: {
        //         authorization: "5240193dbe964e3cbaa210cbaaba108f",
        //         "content-type": "application/json",
        //         "transfer-encoding": "chunked",
        //     },
        //     });
        var myHeaders = new Headers();
        myHeaders.append("content-type", "application/json");
        myHeaders.append("transfer-encoding", "chunked");
        myHeaders.append("authorization", "5240193dbe964e3cbaa210cbaaba108f");

        console.log(curl);
        fetch('https://api.assemblyai.com/v2/transcript',
        {
            method: 'POST',
            headers: myHeaders,
            body: JSON.stringify({"audio_url": curl})
        }).then(response => response.json())
        .then( res => {
            console.log(res);
            setTx(res);
            let tx = res;
            console.log(tx);
            let stat=res.status
           var timer = setInterval(() => {
            if(stat=="queued"){
                fetch( `https://api.assemblyai.com/v2/transcript/${res.id}`,
        {
            method: 'GET',
            headers: myHeaders
        }).then(response => response.json()).then( res => {
           console.log(res.status);
           stat=res.status;
           tx=res;
           setStatus(res.status);
           console.log(tx,"STATUSINSIDER")
        });
        console.log(stat,"STATUS")
            }
            else if(stat=="completed"){
                
                var words = '';
                var i=0;
                console.log(tx.words)
                for(i=0;i<tx.words.length;i++){
                    words=words+' '+tx.words[i].text;
                    console.log(words);
                }
                console.log(words);
                setAnswers([...answers,words]);
                console.log(answers);
                clearInterval(timer);
                return words;
            }
    }, 10000);
           
        });

        
        
            
        //  assembly
        //         .post("/transcript", {
        //             audio_url: curl,
        //         })
        //         .then((res) => {console.log(res.data.id);
                    
                    
        //         })
        //         .catch((err) => console.error(err));
            
        
        
        //    console.log('Here');
       });

       {/*.then(fetch('#', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
           'cache-control': 'no-cache'
         },
         body: JSON.stringify({imgurl:imgurl})
       }).then(async r => {
         let response = await r;
         
         console.log(response.status);  
         console.log(response.body)
     }).catch(err=>console.log(err))
 ).catch(err=>console.log(err));*/}

}

    const getTranscription = async () => {
        try {
          const info = await FileSystem.getInfoAsync(recording.getURI());
          console.log(`AUDIO FILE: ${JSON.stringify(info)}`);
          const uri = info.uri;
          // Base64 encoding for reading & writing
            const options = { encoding: FileSystem.EncodingType.Base64 };
            // Read the audio resource from it's local Uri
            const data64 = await FileSystem.readAsStringAsync(uri, options);
            let wordss = await _publish(data64,uri);
            console.log(wordss);
            setCount(count+1);
            setValues(...values,wordss);
          
          const formData = new FormData();
          formData.append('file', {
            uri,
            type: 'audio/x-wav',
            name: 'recording'
          });
        //   const response = await fetch('https://us-central1-spider-ebtesam.cloudfunctions.net/audio/upload', {
        //     method: 'POST',
        //     body: formData
        //   });
        //   const data = await response.json();
        //   console.log(data.uri);
        //   SetRecordedURI(data.uri);
        }
        catch(error) {
            console.log('Sorry,', error);
          }
        
        
    }

	async function stopRecording() {
		console.log("Stopping recording..");
		setRecording(undefined);
		await recording.stopAndUnloadAsync();
		const uri = recording.getURI();
		console.log("Recording stopped and stored at", uri);
        SetRecordedURI(uri);
        PlayRecordedAudio(uri);
		console.log("uploading");
        getTranscription();
		// const params = { Bucket: "equiteach", Key: "test.mp4", Body: uri };
		// AWS.config.update({
		//   accessKeyId: "AKIATWJ3NAZ7UTZOBQHN",
		//   secretAccessKey: "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",
		//   region: "global",
		// });
		// const s3 = new AWS.S3();
		// // s3.upload(params, (err) => console.log(err));
		// await uploadAudioAsync(uri);
		// try {
		// 	const response = await RNS3.put(file, options);
		// 	if (response.status === 201) {
		// 		console.log("Success: ", response.body);
		// 		/**
		// 		 * {
		// 		 *   postResponse: {
		// 		 *     bucket: "your-bucket",
		// 		 *     etag : "9f620878e06d28774406017480a59fd4",
		// 		 *     key: "uploads/image.png",
		// 		 *     location: "https://your-bucket.s3.amazonaws.com/uploads%2Fimage.png"
		// 		 *   }
		// 		 * }
		// 		 */
		// 	} else {
		// 		console.log("Failed to upload image to S3: ", response);
		// 	}
		// } catch (error) {
		// 	console.log(error);
		// }
	}

    const _submitSurvey = () => {
        var myHeaders = new Headers();
myHeaders.append("Content-Type", "application/json");

var i =0;
var a = [];
for(i=0;i<answers.length;i++){
    a.push({"questionid":i+2,"answer":answers[i]});
}

var raw = JSON.stringify({
  "action": "answersurvey",
  "userid": "7",
  "surveyid": id,
  "answers": a
});

var requestOptions = {
  method: 'POST',
  headers: myHeaders,
  body: raw,
  redirect: 'follow'
};

fetch("https://us-central1-aiot-fit-xlab.cloudfunctions.net/surveydonkey", requestOptions)
  .then(response => response.json())
  .then(result => {console.log(result.points); setPoints(result.points)})
  .catch(error => console.log('error', error));
    }

    // Function to play the recorded audio
  const PlayRecordedAudio = async (uri) => {
    try {
      // Load the Recorded URI
      await AudioPlayer.current.loadAsync({ uri: uri }, {}, true);

      // Get Player Status
      const playerStatus = await AudioPlayer.current.getStatusAsync();

      // Play if song is loaded successfully
      if (playerStatus.isLoaded) {
        if (playerStatus.isPlaying === false) {
          AudioPlayer.current.playAsync();
          SetIsPLaying(true);
        }
      }
    } catch (error) {}
  };

  // Function to stop the playing audio
  const StopPlaying = async () => {
    try {
      //Get Player Status
      const playerStatus = await AudioPlayer.current.getStatusAsync();

      // If song is playing then stop it
      if (playerStatus.isLoaded === true)
        await AudioPlayer.current.unloadAsync();

      SetIsPLaying(false);
    } catch (error) {}
  };

  const viewForm = questions.questions.map((data)=>{
      return(
  <View style={{paddingHorizontal:'5%'}}>
  <Text style={{fontWeight:'bold', color:"#1774FF"}}>{data.text}</Text>
  <View style={{backgroundColor:"#afcdfa", borderRadius:10, paddingVertical:10, paddingHorizontal:'5%', flexDirection:'row', justifyContent:'space-between' }}>
      <TextInput style={{color:"#1774FF", fontWeight:'bold'}} placeholder={''} value={answers[parseInt(data.id)-1]}></TextInput>
      
  </View>
</View>)})

	return (
		<View style={{paddingHorizontal:'5%', paddingTop:'10%'}}>
            <View style={{flexDirection:'row', justifyContent:'space-between'}}>
                <View style={{flexDirection:'row'}}>
                <Icon name="chevron-left" type="entypo" color="#1774FF"></Icon>
                <Text style={{fontWeight:'bold',color:'#1774FF', textAlignVertical:'center'}}>Survey</Text>
                </View>
                <View style={{flexDirection:'row'}}>
                <Icon name="coins" type="font-awesome-5" color={"#1774FF"} size={15}></Icon>
                <Text style={{fontWeight:'bold',color:'#1774FF'}}>100</Text>
                </View>
            </View>
            <Text style={{fontWeight:'bold',color:'#1774FF', textAlignVertical:'center', fontSize:26, textAlign:'center', marginBottom:'5%'}}>{title}</Text>
            
            {viewForm}
            
            <View style={{paddingHorizontal:'5%'}}>
            <Text style={{fontWeight:'bold',color:'#1774FF', textAlign:'center', fontSize:12, marginVertical:'5%'}}>Record Answer {(count+1).toString()}</Text>
            </View>

            {/* <TouchableOpacity onPress={recording ? stopRecording : startRecording}><Text>{recording ? "Stop Recording" : "Start Recording"}</Text></TouchableOpacity>
            <Button
                title={IsPLaying ? "Stop Sound" : "Play Sound"}
                color={IsPLaying ? "red" : "orange"}
                onPress={IsPLaying ? StopPlaying : PlayRecordedAudio}
            />
            <Text>{RecordedURI}</Text> */}
            <TouchableOpacity onPress={recording ? stopRecording : startRecording}><Icon name={recording ?"controller-stop":"mic" }type="entypo" color={"#1774FF"}></Icon></TouchableOpacity>
            <Image source={require('../assets/logo.png')} style={{opacity:0.2, alignSelf:'center'}}></Image>
            <TouchableOpacity onPress={()=>_submitSurvey()}><View style={{borderRadius:10, backgroundColor:"#1774FF", paddingVertical:20, width:'90%', alignSelf:'center', marginTop:'5%'}}>
                <Text style={{textAlign:'center', fontWeight:'bold', color:"#FFF"}}>Submit</Text>
            </View></TouchableOpacity>
            {points>0&&<Text style={{fontWeight:'bold',color:'#1774FF', textAlign:'center', fontSize:12, marginVertical:'5%'}}>+{(points).toString()} points earned!</Text>}
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