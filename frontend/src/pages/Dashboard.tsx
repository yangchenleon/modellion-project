import { Card, Col, Row, Statistic, Table, Typography } from "antd";
import { useEffect, useState } from "react";
import { api } from "../api";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api.statsOverview(10).then(setData).catch(console.error);
  }, []);

  if (!data) return null;

  return (
    <Row gutter={16}>
      <Col span={6}>
        <Card>
          <Statistic title="产品总数" value={data.products_total} />
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic title="有图" value={data.with_images} />
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic title="无图" value={data.without_images} />
        </Card>
      </Col>
      <Col span={24} style={{ marginTop: 16 }}>
        <Card title="最近导入">
          <Table
            rowKey="id"
            size="small"
            dataSource={data.recent}
            columns={[
              { title: "名称", dataIndex: "product_name" },
              { title: "价格", dataIndex: "price" },
              { title: "发布日期", dataIndex: "release_date" },
              { title: "标签", dataIndex: "product_tag" },
              { title: "系列", dataIndex: "series" },
            ]}
            pagination={false}
          />
        </Card>
      </Col>
    </Row>
  );
}
