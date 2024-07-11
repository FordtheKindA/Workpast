#โค้ดตัวนี้เป็นส่วนที่ผมดำเนินการต่อจากพี่ๆในทีมในส่วน Web Development(Deploy&Redeploy) ซึ่งไม่ได้เอาตัวโค้ดทั้งหมดมา เอาเเค่ในส่วนที่ผมดำเนินการมาครับ

1.Deploy Model - การอัพโหลดเเละจัดเก็บผลลัพธ์การเทรน
2.ReDeploy Model - การเเจ้งเตือนสถานะ

#การเลือกชื่อโมเดลเเละการกรอกเวอร์ชั่นของโมเดล
<v-dialog  v-model="dialogModel"  max-width="500">
      <v-toolbar color="primary" dark>            
            <v-toolbar-title>
              Model Settings
            </v-toolbar-title>
          </v-toolbar>
        <v-card>
          <v-card-text style="padding: 20px ;">
            <v-select
            label ="Model Name"
            :items = config
            item-text="val"
            item-value="val"
            v-model = "model_name"
            
            >
          </v-select>

            <v-text-field
              label="Model Version"
              v-model="model_version"
              :rules="[(v) => !!v || 'Model Version is Number required']"
              type="number"
              min="1"
              ></v-text-field>
          </v-card-text>


          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="green darken-1"  text @click="dialog2 = !dialog2">
              
              Deploy
            </v-btn> 
            
          </v-card-actions>
        </v-card>
      </v-dialog>

#เเสดงผลลัพธ์กระบวนการ Deploy Model
  <v-dialog  persistent v-model="dialog3" max-width="800">
    <v-toolbar color="primary" dark>          
          <v-toolbar-title>
            Result of Deploy Model
          </v-toolbar-title>
        </v-toolbar>
        <v-card>
          <v-card-title class="text-center" style="width:100%"
                >            
                <span class="text-center" style="width:100%"> 
                  Model: {{ model_name }} , Version: {{ model_version }}, ID: {{ train_id }} , Name: {{ train_name }} 
                    <p v-if="trainstatus=='true'"><b>Has been successfully deployed</b></p>
                    <p v-else-if="trainstatus =='false'"><b> Unsuccessfully deployed due to server error </b></p>  
                    <p v-else><b>{{ modelExist }}  </b></p>  
                   </span>                   
                  </v-card-title
              >
#เเสดง             
             <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="green darken-1" text @click="dialog3 = !dialog3;dialog2= !dialog2;dialogModel=!dialogModel">
                OK
              </v-btn>
            </v-card-actions>
        </v-card>
      </v-dialog>
#เเสดงการยืนยันที่จะเข้ากระบวนการ deploy model
      <v-dialog  persistent v-model="dialog2" max-width="500">
      <v-toolbar color="primary" dark>            
            <v-toolbar-title>
              Confirm to deploy model?
            </v-toolbar-title>
          </v-toolbar>
          <v-card>
            <v-card-title class="text-center" style="width:100%"
              >            
              <span class="text-center" style="width:100%"> 
                Model: {{ model_name }} , Version: {{ model_version }},<br>
                ID: {{ train_id }} , Name: {{ train_name }} </span>
              </v-card-title
            >
            <v-card-text> </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="red darken-1" text @click="dialogModel = !dialogModel; dialog2 = !dialog2"> No </v-btn>
              <v-btn color="green darken-1" text @click="updateConfigAndDownloadFile">
                Yes,Confirm IT
              </v-btn>
              
            </v-card-actions>
          </v-card>
        </v-dialog>
#เเสดงการรอกระบวนการการ Deploy model (เเบบหมุนเป็นวงกลม)
        <v-dialog v-model="isProgress" persistent width="150" height="150" >
          <v-card>
              <v-card-title class="text-center" style="width:100%"
                >            
                <span class="text-center" style="width:95%"> 
                                    <v-progress-circular :size = '100' :width="5"   indeterminate      color="primary"    ></v-progress-circular>
</span>
                </v-card-title
              >
              <v-card-text> </v-card-text>
            </v-card>          
        </v-dialog>

#เเสดงผลลัพธ์กระบวนการ Redeploy Model
        <v-dialog v-model="dialog4" persistent max-width="800">
        <v-toolbar color="primary" dark>            
              <v-toolbar-title>
                Redeploy Model Result
              </v-toolbar-title>
            </v-toolbar>
            <v-card>
              <v-card-title class="text-center" style="width:100%"
                >            
                <span class="text-center" style="width:100%" > 
                  {{ res_message }} 
<p v-if="trainstatus"><b>Has been successfully deployed</b></p>
                      <p v-else><b> Unsuccessfully deployed from</b></p>   </span>
                  
                </v-card-title
              >
              <v-card-text> </v-card-text>
              <v-col class="text-right">
              <v-btn align="right" color="green darken-1" text @click="closeModel()" >
                  OK
              </v-btn>
              </v-col>
            </v-card>
          </v-dialog>


<script>
import { mapState, mapActions, mapMutations } from "vuex";
import { formatAxiosError } from "@/utils/common";
import moment from "moment";
import axios from "axios";
import { version } from "vue";
export default {
  data() {
    return {
      description: "",
      modelAuthor: null,
      modelVersion: null,
      trainRecipe: null,
      loadWeights: "NONE",
      trainRecipeData: [],
      trainerList: [],
      currentSelectedTrainer: {},
      currentSelectedTrain: {},
      checkJson: "",
      dialogJson: false,
      trainidLoading: false,
      train_id: "",
      dialogModel: false,
      status: "deployed",
      search: "",
      model_name: "cdsem_au",
      model_version: "",
      resultSuccess: "",
      trainData: [],
      trainHead: [
        { text: "Train ID", value: "train_id", align: "center" },
        { text: "Train Name", value: "train_name" },
        { text: "Trainer", value: "trainer", align: "center" },
        { text: "Model", value: "model_fullname", align: "center" },
        { text: "Creator", value: "gid", align: "center" },
        { text: "Status", value: "status", align: "center" },
        { text: "Detail", value: "info", align: "center" },
        {
          text: "Deploy",
          value: "action",
          align: "center",
          class: "row_margin",
        },
      ],
      showinfo: false,
      dialog: false,
      dialog2: false,
      dialog3: false,
      url: null,
      interval: null,
      train_name: "",
      config: "",
      trainSuccess: false,
      trainstatus: "",
      object_url: "",
      model_path: "",
      name_get: "",
      isProgress: false,
      dialog4: false,
      res_message: "",
      modelExist: "",
    };
  },
  created() {
    this.setProcess(this.$store.getters.process);
    this.getTrainData();
    this.getTrainerList();
    this.doFetchTrainRecipe();
    this.doFetchLoadWeights();
    this.interval = setInterval(() => this.getTrainData(), 10000);
    this.getNameAndPath();
  },

// HTTP GET ข้อมูลที่เกี่ยวข้อง
  methods: {getNameAndPath() {
      axios
        .get(
          this.$store.getters.service_url +
            "/lookup/" +
            this.$store.getters.process +
            "/model_name?sort_by=model_name"
        )
        .then((res) => {
          this.config = res.data.data;
          console.log(res.data.data);
          this.name_get = res.data.data;
        })
        .catch((err) => {
          this.config = [];
          console.log(err); // Errors
        });
    },
    getModelsFile(item) {
      this.dialogModel = true;
      this.train_id = item.train_id;
      this.train_name = item.train_name;

      axios
        .get(
          this.$store.getters.service_url +
            "/train/" +
            this.$store.getters.process +
            "/results?train_id=" +
            item.train_id +
            "&object_name=models"
        )
        .then((res) => {
          this.object_url = res.data.data[0].object_url;
          //this.config = res.data.data;
          console.log(res.data.data);
        })
        .catch((err) => {
          //this.config = [];
          console.log(err); // Errors
        });
    },
//HTTP POST DEPLOY MODEL PROCESS ตรงลิ้งต่างๆขอปิดไว้เนื่องจากเป็นของบริษัท
    updateConfigAndDownloadFile() {
      this.name_get.forEach((items) => {
        if (items.val == this.model_name) {
          this.model_path = items.description;
        }
        this.isProgress = true;
      });
      axios
        .post(
          "http://xxxxxxxx/apitest",
          {
            timeout: 5000,
          },
          {
            model_url: this.object_url,
            //model_path: `\\data\\poc\\models\\${this.model_name}`,
            model_path: this.model_path,
            config_url:
              "https://xxxxxxxxxxxxx",
            config_path: "\\data\\poc\\models",
            config_name: "models.CONF",
            model_name: this.model_name,
            model_version: this.model_version,
            gid: this.$store.getters.gid,
            message:
              "Deploy model name" +
              this.model_name +
              " Version " +
              this.model_version +
              " by " +
              this.$store.getters.user_name,
          }
        )
        .then((res) => {
          console.log(res.data);
          if (res.message == "Network Error") {
            this.trainstatus = "error";
            this.modelExist = res.message;
          } else {
            if (res.data.status == "Success") {
              this.trainstatus = true;
              this.isProgress = false;
              this.dialog3 = true;
              this.ReDeploy();
              this.dialog4 = true;
            } else {
              this.trainstatus = false;
              this.isProgress = false;
              this.dialog3 = true;
            }
            this.resultSuccess = res.data.status;
            console.log(res.data.status);
          }
        })
        .catch((err) => {
          if (err.code == "ERR_NETWORK") {
            this.isProgress = false;
            this.trainstatus = "error";
            this.modelExist = "Unsuccess Deploy due to Server Time Out";
            this.dialog3 = true;
          }
          console.log("error" + err.code); // Errors
        });
    },
//HTTP PUT เพื่ออัพเดทข้อมูล
    updatestatus() {
      axios
        .put(
          this.$store.getters.service_url +
            "/train/" +
            this.$store.getters.process +
            "/master",
          {
            train_id: this.train_id,
            status: "complete",
          }
        )
        .then((res) => {
          console.log(res.data);
        })
        .catch((err) => {
          console.log(err); // Errors
        });
    },
//HTTP POST REDEPLOY MODEL PROCESS ตรงลิ้งต่างๆขอปิดไว้เนื่องจากเป็นของบริษัท
    ReDeploy() {
      axios
        .post(
          "http://xxxxxxxxxx",
          {
            gid: this.$store.getters.gid,
            message:
              "Deploy model name" +
              this.model_name +
              " Version " +
              this.model_version +
              " by " +
              this.$store.getters.user_name,
          }
        )
        .then((res) => {
          console.log(res.data);
          this.res_message = res.data.message;
        })
        .catch((err) => {
          alert(err); // Errors
        });
    },
//SET CLOSE ALL DIALOGBOX - BUG REPAIR
    closeModel() {
      this.dialog4 = !this.dialog4;
      this.dialog3 = !this.dialog3;
      this.dialog2 = !this.dialog2;
      this.dialogModel = !this.dialogModel;
    },
},
};
</script>