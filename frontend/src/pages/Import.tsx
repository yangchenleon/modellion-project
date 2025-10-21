import { Button, Card, List, message } from "antd";
import { useState } from "react";
import { api } from "../api";

export default function ImportPage() {
  const [report, setReport] = useState<any>(null);

  const run = async () => {
    try {
      const res = await api.importFromJson();
      setReport(res);
      message.success(`导入完成，新增 ${res.created}，更新 ${res.updated}`);
    } catch (e: any) {
      message.error(e.message || "导入失败");
    }
  };

  return (
    <Card title="批量导入 JSON">
      <p>从后端 DATA_DIR 下的 product_details.json 读取并 UPSERT（按 URL）。</p>
      <Button type="primary" onClick={run}>执行导入</Button>
      {report && (
        <div style={{ marginTop: 16 }}>
          <div>总数：{report.total}，新增：{report.created}，更新：{report.updated}</div>
          {report.errors?.length ? (
            <>
              <div>错误：</div>
              <List size="small" bordered dataSource={report.errors} renderItem={(i) => <List.Item>{i}</List.Item>} />
            </>
          ) : null}
        </div>
      )}
    </Card>
  );
}
