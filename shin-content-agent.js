require('dotenv').config();
const Anthropic = require("@anthropic-ai/sdk");
const fs = require('fs');
const path = require('path');

if (!process.env.ANTHROPIC_API_KEY) {
  console.error('❌ 오류: ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.');
  console.error('해결: .env 파일을 만들고 ANTHROPIC_API_KEY="sk-..." 를 입력하세요.');
  process.exit(1);
}

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

// 시즌 키워드 정의
const seasonKeywords = {
  1: ["신년목표", "작심삼일", "새해계획"],
  2: ["자존감", "사랑", "밸런타인"],
  3: ["이직", "새출발", "봄"],
  4: ["번아웃", "벚꽃", "활동"],
  5: ["가정의달", "부모", "감사"],
  6: ["상반기결산", "여름준비"],
  7: ["건강", "여름", "휴가준비"],
  8: ["휴가", "리셋", "자존감"],
  9: ["자기계발", "새학기", "준비"],
  10: ["독서", "가을", "성찰"],
  11: ["연말준비", "감사", "회고"],
  12: ["회고", "감사", "새해준비"],
};

// 캐릭터 프로필
const characters = {
  노박: {
    age: 72,
    gender: "남성",
    job: "데이터 전략가",
    tone: "차분하고 지혜로운",
    strength: ["자기계발", "동기부여", "돈", "습관", "인생조언"],
  },
  순이: {
    age: 68,
    gender: "여성",
    job: "전직 간호사",
    tone: "따뜻하고 포근한",
    strength: ["건강", "힐링", "가족", "위로", "마음챙김"],
  },
  준혁: {
    age: 45,
    gender: "남성",
    job: "AI 엔지니어",
    tone: "날카롭고 논리적인",
    strength: ["기술", "AI", "미래", "직장생활", "재테크"],
  },
  세아: {
    age: 42,
    gender: "여성",
    job: "디자이너",
    tone: "감성적이고 세련된",
    strength: ["라이프스타일", "인테리어", "자존감"],
  },
  루민: {
    age: 17,
    gender: "남성",
    job: "고등학생",
    tone: "호기심 많고 솔직한",
    strength: ["공부", "학교생활", "진로"],
  },
  하린: {
    age: 14,
    gender: "여성",
    job: "중학생",
    tone: "밝고 당찬",
    strength: ["꿈", "우정", "성장"],
  },
  도트: {
    age: 13,
    gender: "남성",
    job: "막내",
    tone: "유머러스하고 엉뚱한",
    strength: ["개그", "반전", "일상유머"],
  },
};

// 1단계: 트렌드 분석 (시즌 기반 주제 추천)
async function analyzeTrends(category = "전체", targetAge = "전연령") {
  const today = new Date();
  const month = today.getMonth() + 1;
  const seasonTags = seasonKeywords[month] || [];

  const prompt = `
당신은 YouTube Shorts 콘텐츠 트렌드 분석가입니다.

현재: ${today.getFullYear()}년 ${month}월
시즌 키워드: ${seasonTags.join(", ")}
카테고리: ${category}
타겟 연령: ${targetAge}

위 조건을 고려하여 **이 주에 만들면 잘 나갈 YouTube Shorts 주제 3개**를 추천해주세요.

각 주제마다:
1) 주제 제목 (한 줄)
2) 트렌드 근거 (왜 지금 뜨는지)
3) 예상 조회수 (상/중/하)
4) 경쟁도 (🟢블루오션/🟡경쟁있음/🔴레드오션/💎틈새)
5) 추천 캐릭터 이름 (노박/순이/준혁/세아/루민/하린/도트 중 1명)
6) 추천 톤 (동기부여/힐링/유머/교육/감동)

JSON 형식으로 반환하세요:
{
  "trends": [
    {
      "title": "",
      "reason": "",
      "expectedViews": "",
      "competition": "",
      "character": "",
      "tone": ""
    }
  ]
}
`;

  const response = await client.messages.create({
    model: "claude-opus-4.6",
    max_tokens: 1000,
    messages: [{ role: "user", content: prompt }],
  });

  return JSON.parse(response.content[0].text);
}

// 2단계: 주제 선택 후 대본 생성
async function generateScript(
  topic,
  character,
  tone,
  length = "60초",
  isCollab = false
) {
  const charInfo = characters[character];

  const prompt = `
당신은 YouTube Shorts 대본 작가입니다.

주제: ${topic}
캐릭터: ${character} (${charInfo.tone} 말투, ${charInfo.job})
톤: ${tone}
길이: ${length}
협업모드: ${isCollab ? "2명 대화 형식" : "캐릭터 독백"}

다음 형식으로 60초 Shorts 대본을 작성하세요:

[오프닝 (0~2초)]
걸음이 로고 애니메이션 설명

[캐릭터 등장 (2~5초)]
${character}의 시그니처 등장 음악/춤사위

[본편 (5~${length === "30초" ? "25" : length === "60초" ? "55" : "85"}초)]
장면1: [대사]
장면2: [대사]
... (2~3개 장면)

[CTA (마지막 5초)]
댓글 유도 질문

각 부분을 명확히 구분하고, 장면별로 영상 제작에 필요한 시각적 설명도 포함하세요.
`;

  const response = await client.messages.create({
    model: "claude-opus-4.6",
    max_tokens: 2000,
    messages: [{ role: "user", content: prompt }],
  });

  return response.content[0].text;
}

// 3단계: 멀티플랫폼 메타데이터 생성
async function generateMetadata(
  topic,
  character,
  scriptPreview,
  length = "60초"
) {
  const prompt = `
YouTube Shorts 메타데이터 생성자입니다.

주제: ${topic}
캐릭터: ${character}
길이: ${length}
대본 일부: ${scriptPreview.substring(0, 200)}...

다음을 JSON 형식으로 생성하세요:
{
  "youtube": {
    "title": "(한글, 40자 이내)",
    "description": "(100자 이내)",
    "hashtags": ["#", "#", ...]
  },
  "tiktok": {
    "caption": "(50자 이내)",
    "hashtags": ["#", "#", ...]
  },
  "thumbnail": {
    "text": "(한글, 10자 이내)"
  },
  "cta": {
    "comment": "댓글 유도 질문"
  }
}
`;

  const response = await client.messages.create({
    model: "claude-opus-4.6",
    max_tokens: 1000,
    messages: [{ role: "user", content: prompt }],
  });

  return JSON.parse(response.content[0].text);
}

// 결과를 JSON 파일로 저장
function saveResults(data) {
  const outputDir = path.join(__dirname, 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const today = new Date().toISOString().split('T')[0];
  const filename = path.join(outputDir, `content-${today}.json`);
  
  fs.writeFileSync(filename, JSON.stringify(data, null, 2));
  console.log(`\n💾 결과 저장됨: ${filename}`);
  return filename;
}

// 메인 에이전트 실행
async function runDailyContentAgent() {
  console.log("\n=== 📺 SHIN FAMILY 일일 콘텐츠 생성 에이전트 ===\n");

  try {
    // Step 1: 트렌드 분석
    console.log("📊 Step 1: 트렌드 분석 중...");
    const trends = await analyzeTrends("자기계발", "전연령");
    console.log("✓ 트렌드 분석 완료\n");
    console.log("추천 주제:");
    trends.trends.forEach((t, i) => {
      console.log(
        `${i + 1}. ${t.title} (${t.character}) - ${t.competition}`
      );
    });

    // Step 2: 첫 번째 주제 선택 → 대본 생성
    const selected = trends.trends[0];
    console.log(`\n✍️ Step 2: "${selected.title}" 대본 생성 중...`);
    const script = await generateScript(
      selected.title,
      selected.character,
      selected.tone,
      "60초",
      false
    );
    console.log("✓ 대본 생성 완료\n");
    console.log("생성된 대본:");
    console.log(script.substring(0, 500) + "...\n");

    // Step 3: 메타데이터 생성
    console.log("🏷️ Step 3: 메타데이터 생성 중...");
    const metadata = await generateMetadata(
      selected.title,
      selected.character,
      script,
      "60초"
    );
    console.log("✓ 메타데이터 생성 완료\n");
    console.log("YouTube 메타:");
    console.log(`제목: ${metadata.youtube.title}`);
    console.log(`설명: ${metadata.youtube.description}`);
    console.log(`태그: ${metadata.youtube.hashtags.join(" ")}\n`);

    // 결과 요약
    console.log("=== 📋 오늘의 콘텐츠 패키지 ===");
    console.log(`주제: ${selected.title}`);
    console.log(`캐릭터: ${selected.character}`);
    console.log(`톤: ${selected.tone}`);
    console.log(`CTA: ${metadata.cta.comment}`);
    console.log(
      "\n✨ 이 대본과 메타데이터로 바로 촬영 + 편집 준비 가능합니다!"
    );

    // 결과 저장
    const results = {
      timestamp: new Date().toISOString(),
      trends: trends.trends,
      selectedTopic: selected,
      script: script.substring(0, 500),
      metadata: metadata
    };
    
    saveResults(results);
  } catch (error) {
    console.error("에이전트 실행 오류:", error);
  }
}

// 실행
runDailyContentAgent();
