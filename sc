git clone https://github.com/iamthehimansh/STRIVER-JUDGE.git
cd STRIVER-JUDGE
<!-- python3 scripts/restore_data.py                                   # stitch .partNNN → .jsonl -->
docker build -t striver-judge:latest -f judge/Dockerfile .        # sandbox image
docker compose up -d --build                                      # app on :3000
npm install
npm run dev