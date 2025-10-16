# Magic Metronome | 魔法节拍器
> 一款能感知乐手节奏起伏、自动调整拍速的“智能海螺”，帮助练习更贴合真实演奏。  
> A smart metronome that senses tempo drift and adapts in real time.

## 🧠 问题陈述 Problem Statement
- 独自练习的乐手常因紧张或情绪导致速度漂移，传统节拍器无法反馈。  
  Solo musicians drift tempo due to nerves; classic metronomes stay rigid.
- 远程合奏时，难以根据彼此呼吸节奏调整，更难协作。  
  Remote sessions lack shared breathing cues for alignment.

## 🎯 目标用户 Target Users
- 需要日常练习的学生与业余乐手。  
  Students and hobbyists practicing daily.
- 需要远程排练的室内乐团、乐队成员。  
  Chamber groups and bands rehearsing remotely.

## 🔍 核心洞察 Key Insight
- 通过设备麦克风与打击输入，可估算实时 BPM 波动。  
  Mic input plus tap sensors can estimate live BPM swings.
- 给予“弹性节拍”反馈能帮助乐手感知并修正习惯性偏差。  
  Elastic tempo guidance may correct habitual drift.

## 💡 初步方案 Sketch Solution
- 通过 Web App + 外接或内置麦克风检测节奏。  
  Web app using built-in/external mic.
- 动态调节节拍器速度，并以颜色/语音提示偏差。  
  Adjusts beats dynamically with color/voice cues.
- 提供练习回放曲线，显示平均 BPM 与波动范围。  
  Offers practice playback curves of BPM and variance.

## ⚙️ 技术可行性 Technical Feasibility
- Web Audio API 捕捉与分析波形。  
  Use Web Audio API for waveform analysis.
- 简易节奏检测可用 autocorrelation + peak detection。  
  Tempo detection via autocorrelation and peak detection.
- 前端：React/Vite；后端暂定 Serverless 统计。  
  Frontend React/Vite; optional serverless analytics.

## 📏 成功指标 Success Metrics
- 10 名测试用户在 2 周内节拍偏差降低 30%。  
  10 testers reduce tempo drift by 30% in 2 weeks.
- 远程合奏实验满意度 >80%。  
  Remote rehearsal satisfaction >80%.
- 练习回放功能开放后，用户留存率 >60%。  
  Playback feature drives >60% retention.

## ⚠️ 风险与反例 Risks & Counterpoints
- 噪音环境导致识别不准。  
  Noisy environments may skew detection.
- 与现有智能节拍器（Soundbrenner 等）差异不足。  
  Differentiation vs. existing smart metronomes is unclear.
- 远程合奏需要低延迟音频，技术门槛高。  
  Low-latency audio for remote play is complex.

## 🧱 MVP 范围 MVP Scope
- 仅支持单人练习，提供基础动态节拍器与练习曲线。  
  Solo practice only; adaptive beat plus simple graphs.
- 计划 3 周完成：  
  Timeline (3 weeks):
  - 第 1 周：节拍检测 & UI 草图  
    Week 1: tempo detection + UI mock.
  - 第 2 周：实时反馈与曲线可视化  
    Week 2: live feedback and charts.
  - 第 3 周：封闭测试 & 反馈迭代  
    Week 3: closed testing and iterations.

## 🤝 需要的协作者 Needed Collaborators
- 音频信号处理顾问 1 名。  
  Audio signal processing mentor.
- 前端工程师 1-2 名。  
  1–2 frontend engineers.
- 乐手测试志愿者若干。  
  Volunteer musicians for testing.

## 🔗 参考资料 References
- <https://developer.mozilla.org/docs/Web/API/Web_Audio_API>  
- Soundbrenner 波形控制：<https://www.soundbrenner.com/>  
- 远程合奏案例：<https://lofi-broadcast-labs.example.com> *(虚拟示例)*  
