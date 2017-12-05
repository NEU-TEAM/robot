#include "ros/ros.h"
#include "std_msgs/String.h"

#include "/robot/inc/qtts.h"
#include "/robot/inc/msp_cmn.h"
#include "/robot/inc/msp_errors.h"

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

using namespace std;

const char* synthesized_voice = "/robot/wav/synthesizedVoice.wav";
const char* params_of_synthesized_voice = "engine_type = local, text_encoding = UTF8, tts_res_path = fo|/robot/msc/res/tts/xiaoyan.jet;fo|/robot/msc/res/tts/common.jet, sample_rate = 16000, speed = 50, volume = 50, pitch = 50, rdn = 0";

typedef struct _wave_pcm_hdr
{
  char		riff[4];
  int			size_8;
  char		wave[4];
  char		fmt[4];
  int			fmt_size;
  short int	format_tag;
  short int	channels;
  int			samples_per_sec;
  int			avg_bytes_per_sec; 
  short int	block_align;
  short int	bits_per_sample;
  char 		data[4];
  int 		data_size;
} wave_pcm_hdr;

wave_pcm_hdr default_wav_hdr = 
{
  { 'R', 'I', 'F', 'F' },
  0,
  {'W', 'A', 'V', 'E'},
  {'f', 'm', 't', ' '},
  16,
  1,
  1,
  16000,
  32000,
  2,
  16,
  {'d', 'a', 't', 'a'},
  0  
};

/* 文本合成 */
int text_to_voice(const char* src_text, const char* des_path, const char* params)
{
  int          ret          = -1;
  FILE*        fp           = NULL;
  const char*  sessionID    = NULL;
  unsigned int audio_len    = 0;
  wave_pcm_hdr wav_hdr      = default_wav_hdr;
  int          synth_status = MSP_TTS_FLAG_STILL_HAVE_DATA;
  
  if (NULL == src_text || NULL == des_path)
  {
    printf("params is error!\n");
    return ret;
  }
  fp = fopen(des_path, "wb");
  if (NULL == fp)
  {
    printf("open %s error.\n", des_path);
    return ret;
  }
  /* 开始合成 */
  sessionID = QTTSSessionBegin(params, &ret);
  if (MSP_SUCCESS != ret)
  {
    printf("QTTSSessionBegin failed, error code: %d.\n", ret);
    fclose(fp);
    return ret;
  }
  ret = QTTSTextPut(sessionID, src_text, (unsigned int)strlen(src_text), NULL);
  if (MSP_SUCCESS != ret)
  {
    printf("QTTSTextPut failed, error code: %d.\n",ret);
    QTTSSessionEnd(sessionID, "TextPutError");
    fclose(fp);
    return ret;
  }
  //printf("正在合成 ...\n");
  fwrite(&wav_hdr, sizeof(wav_hdr) ,1, fp); //添加wav音频头，使用采样率为16000
  while (true) 
  {
    /* 获取合成音频 */
    const void* data = QTTSAudioGet(sessionID, &audio_len, &synth_status, &ret);
    if (MSP_SUCCESS != ret)
      break;
    if (NULL != data)
    {
      fwrite(data, audio_len, 1, fp);
      wav_hdr.data_size += audio_len; //计算data_size大小
    }
    if (MSP_TTS_FLAG_DATA_END == synth_status)
      break;
  }//合成状态synth_status取值请参阅《讯飞语音云API文档》
  printf("\n");
  if (MSP_SUCCESS != ret)
  {
    printf("QTTSAudioGet failed, error code: %d.\n",ret);
    QTTSSessionEnd(sessionID, "AudioGetError");
    fclose(fp);
    return ret;
  }
  /* 修正wav文件头数据的大小 */
  wav_hdr.size_8 += wav_hdr.data_size + (sizeof(wav_hdr) - 8);
  
  /* 将修正过的数据写回文件头部,音频文件为wav格式 */
  fseek(fp, 4, 0);
  fwrite(&wav_hdr.size_8,sizeof(wav_hdr.size_8), 1, fp); //写入size_8的值
  fseek(fp, 40, 0); //将文件指针偏移到存储data_size值的位置
  fwrite(&wav_hdr.data_size,sizeof(wav_hdr.data_size), 1, fp); //写入data_size的值
  fclose(fp);
  fp = NULL;
  /* 合成完毕 */
  ret = QTTSSessionEnd(sessionID, "Normal");
  if (MSP_SUCCESS != ret)
  {
    printf("QTTSSessionEnd failed, error code: %d.\n",ret);
  }
  
  return ret;
}

void xf_tts_callback(const std_msgs::String::ConstPtr& msg)
{
  int         ret                  = MSP_SUCCESS;
  const char* login_params         = "appid =57331875, work_dir = .";//登录参数,appid与msc库绑定,请勿随意改动
  const char* session_begin_params = params_of_synthesized_voice;
  /* 用户登录 */
  ret = MSPLogin(NULL, NULL, login_params); //第一个参数是用户名，第二个参数是密码，第三个参数是登录参数，用户名和密码可在http://open.voicecloud.cn注册获取
  if (MSP_SUCCESS != ret)
  {
    printf("MSPLogin failed, error code: %d.\n", ret);
    goto exit ;//登录失败，退出登录
  }
  /* 文本合成 */
  ret = text_to_voice(msg->data.c_str(), synthesized_voice, session_begin_params);
  if (MSP_SUCCESS != ret)
  {
    printf("text_to_voice failed, error code: %d.\n", ret);
  }
  ros::param::set("is_ready_to_play",true);
exit:
  MSPLogout(); //退出登录
}

int main(int argc,char **argv)
{
  ros::init(argc,argv,"text_to_voice");
  ros::NodeHandle n;
  ros::Subscriber pub = n.subscribe("/ctrl/voice/text_to_voice", 10, xf_tts_callback); 
  ros::spin();
  return 0;
}
