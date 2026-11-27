# 折痕 · 纸箱重复折叠寿命筛查

山梧循环搬家纸箱站有两个收箱点和四名收箱、维修和放行值班员。搬家班组把拆平后的箱体连同标签交到站点，站点再把可用箱交给下一条路线。值班员以前用纸本折数和便签记录异常，无法从多项轻微变形识别异常、不知道隔离架是否满位，也容易发出未经本次复检的纸箱。

系统把每只箱的折叠读数、隔离或维修记录、上一轮出入库单对应起来。每次发运凭一条通过的折叠读数，退回后需要新的读数。

| 模块 | 业务职责 |
|---|---|
| 收箱 | 按实体箱体标签建档，固定纸箱规格和站点，维护物理累计折数。 |
| 折叠台 | 录左右定形量、手孔漂移、搭扣力和开裂量。每个箱只接受递增的累计折数。异步分析保留样本摘要和判定来源。 |
| 隔离及维修 | 异常箱进入有容量限制的隔离架。架满时仍保持隔离，在候位区等待；维修登记要求分配架位。至多保留两次维修机会，失败继续留在原案。折数达到记录上限的箱体进入退役通道。 |
| 复检签放 | 操作员重新测量，复核员根据最新复检签放。退役永久停止发运，签放和退役均释放架位。 |
| 发运和归还 | 一箱同一时间只有一张有效发运单。发运单绑定通过读数，归还后原读数无法再次用于发运。 |

| 角色 | 账号 / 口令 | 操作 |
|---|---|---|
| 站点操作员 | `operator` / `operator-hexin-demo` | 建档、测量、维修、复检、发运、收箱 |
| 复核员 | `admin` / `admin-hexin-demo` | 登记基准样本、签字放行、退役、查审计 |
| 搬家班组观察员 | `viewer` / `viewer-hexin-demo` | 查看箱体、测量记录、隔离案和出入库单 |

## 一天的班次

1. 08:00 北站收到累计折数 299 的 `LOOP-N-0408`，仍处于待测状态。
2. 08:15 在 `N-BENCH-02` 录入第 300 折。两侧接近 12 mm 的残余位移和较大的手孔漂移组合被模型判离群，箱体进入 `N-HOLD-01`。
3. 08:25 同站 `LOOP-N-0414` 达到开裂与不对称拦截条件。架位已满，系统留下候位隔离案。
4. 09:00 维修员为 0408 登记胶带修补，操作员在第 302 折复检，值班复核员签放。
5. 10:30 `ROUTE-WEST-4` 按 `OUT-N-0801` 领走 0408，出库单记录支撑放行的复检编号。
6. 11:45 0414 领取刚释放的架位。连做两轮修理和复检仍超限，复核员办理退役。
7. 14:00 路线归还 0408。箱重新进入待测，等下一次读取。

## 启动

```sh
cp .env.example .env
docker compose up -d --build --wait
curl http://127.0.0.1:18367/health
curl http://127.0.0.1:18367/openapi.json
docker compose exec -T backend python -m scripts.seed_demo
```

网关、直连 API 和 PostgreSQL 本机调试端口分别为 `18367`、`19367` 和 `17867`。PostgreSQL 和 Redis 持久卷供同一栈后续运行使用，Redis 和 worker 走内部网络。常规停止运行 `docker compose down`。若明确要重建演示数据库，再加 `-v`。

`.env.example` 有端口、签名口令、数据库口令和 seed 开关。使用 `SEED_DEMO=true` 会自动添加演示账号及样本，重复执行保留已入库的数据。建账口令可通过 `DEMO_ADMIN_PASSWORD`、`DEMO_OPERATOR_PASSWORD` 和 `DEMO_VIEWER_PASSWORD` 注入。

```sh
curl -X POST http://127.0.0.1:18367/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"operator","password":"operator-hexin-demo"}'

curl 'http://127.0.0.1:18367/boxes?depot=north' \
  -H "Authorization: Bearer $TOKEN"
```

| HTTP 操作 | 路径 |
|---|---|
| 箱体建档及时间线 | `POST /boxes`、`GET /boxes/{id}` |
| 折叠台读数 | `POST /boxes/{id}/folds`、`GET /folds/{id}`、`GET /jobs/{id}` |
| 隔离容量与移架 | `GET /quarantine?depot=north`、`POST /quarantine/{id}/rack` |
| 维修、复检和签放 | `POST /quarantine/{id}/repairs`、`POST /boxes/{id}/rechecks`、`POST /quarantine/{id}/release` |
| 退役 | `POST /quarantine/{id}/retire` |
| 发运和归还 | `POST /boxes/{id}/dispatches`、`POST /dispatches/{id}/return` |
| 在役折叠参考集 | `GET /baseline`、`POST /baseline/samples` |

## 模型和证据

每种纸箱规格使用自己的无标签样本。输入向量由折叠次数的 `log1p`、左右变形均值、左右差绝对值、手孔漂移、闭合力和裂纹长度构成。Isolation Forest 用 120 棵树，随机种子 617，每一规格至少需 40 条参考数据。取 `-score_samples` 作为离群分，达到 0.58 触发隔离，独立的站内实测阈值也可触发隔离。完整记录保留实际有效的原因。快照摘要由模型设置、排序后的样本标识和特征生成。模拟数据生成器为两个规格各提供 96 条在役读数。

规格阈值是工作流演示夹具的本地规则。真实纸箱的参考分布和阈值需由自己的试验站校验。此服务记录测量值与业务决定，物理上架、维修和验收由现场人员完成。

FastAPI 和 Nginx 暴露 JSON，PostgreSQL 持久化站点状态与队列，Redis 用于健康和 worker 心跳，scikit-learn 执行分析。领域枚举见 `backend/domain/contracts.py` 和 PostgreSQL 迁移约束，维修上限和实测阈值见 `station_limits.py`。本机调试使用 `docker compose logs -f backend worker`，完整验收见工作区的 `test-artifacts/hexin-0018/TESTING.md`。

MIT 许可。
