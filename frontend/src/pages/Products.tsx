import { Button, Card, Form, Input, Popconfirm, Space, Table, message } from "antd";
import { useEffect, useState } from "react";
import { api } from "../api";
import { useNavigate } from "react-router-dom";

export default function Products() {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<{ items: any[]; meta: any }>({ items: [], meta: { page: 1, page_size: 20, total: 0 } });

  const fetchData = async (page = 1, page_size = 20) => {
    try {
      setLoading(true);
      const params = { ...form.getFieldsValue(), page, page_size } as any;
      const res = await api.getProducts(params);
      setData(res);
    } catch (e: any) {
      message.error(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <Card title="产品列表" extra={<Button type="primary" onClick={() => navigate("/products/0")}>新建</Button>}>
      <Form form={form} layout="inline" onFinish={() => fetchData(1, data.meta.page_size)}>
        <Form.Item name="name" label="名称">
          <Input allowClear placeholder="包含关键词" />
        </Form.Item>
        <Form.Item name="tag" label="标签">
          <Input allowClear />
        </Form.Item>
        <Form.Item name="series" label="系列">
          <Input allowClear />
        </Form.Item>
        <Button type="primary" htmlType="submit">筛选</Button>
      </Form>
      <Table
        style={{ marginTop: 12 }}
        loading={loading}
        rowKey="id"
        dataSource={data.items}
        pagination={{
          current: data.meta.page,
          total: data.meta.total,
          pageSize: data.meta.page_size,
          onChange: (p, s) => fetchData(p, s),
        }}
        columns={[
          { title: "名称", dataIndex: "product_name" },
          { title: "价格", dataIndex: "price" },
          { title: "发布日期", dataIndex: "release_date" },
          { title: "标签", dataIndex: "product_tag" },
          { title: "系列", dataIndex: "series" },
          {
            title: "操作",
            render: (_, r: any) => (
              <Space>
                <Button size="small" onClick={() => navigate(`/products/${r.id}`)}>编辑</Button>
                <Button size="small" onClick={() => navigate(`/images/${r.id}`)}>图片</Button>
                <Popconfirm title="确认删除？" onConfirm={async () => { await api.deleteProduct(r.id); message.success("已删除"); fetchData(data.meta.page, data.meta.page_size); }}>
                  <Button size="small" danger>删除</Button>
                </Popconfirm>
              </Space>
            )
          }
        ]}
      />
    </Card>
  );
}
