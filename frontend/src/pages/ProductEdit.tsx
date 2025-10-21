import { Button, Card, Form, Input, message, Space } from "antd";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";

export default function ProductEdit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isCreate = !id || id === "0";
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isCreate) {
      api.getProduct(Number(id)).then((r) => form.setFieldsValue(r));
    }
  }, [id]);

  const onSubmit = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields();
      if (isCreate) {
        await api.createProduct(values);
        message.success("已创建");
      } else {
        await api.updateProduct(Number(id), values);
        message.success("已保存");
      }
      navigate("/products");
    } catch (e: any) {
      if (e?.message) message.error(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title={isCreate ? "新建产品" : "编辑产品"}>
      <Form form={form} layout="vertical" initialValues={{ product_tag: "", series: "" }}>
        <Form.Item name="product_name" label="名称">
          <Input />
        </Form.Item>
        <Form.Item name="price" label="价格">
          <Input placeholder="例如 2,200円" />
        </Form.Item>
        <Form.Item name="release_date" label="发布日期">
          <Input placeholder="例如 2025-01" />
        </Form.Item>
        <Form.Item name="url" label="URL" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="product_tag" label="标签">
          <Input />
        </Form.Item>
        <Form.Item name="series" label="系列">
          <Input />
        </Form.Item>
        <Form.Item name="article_content" label="正文(HTML)">
          <Input.TextArea rows={6} />
        </Form.Item>
        <Space>
          <Button onClick={() => navigate(-1)}>返回</Button>
          <Button type="primary" loading={loading} onClick={onSubmit}>
            保存
          </Button>
        </Space>
      </Form>
    </Card>
  );
}
