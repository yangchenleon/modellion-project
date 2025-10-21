import { Button, Card, Form, Input, message } from "antd";
import { api } from "../api";
import { setRole, setToken } from "../utils/auth";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    try {
      const res = await api.login(values.username, values.password);
      setToken(res.access_token);
      const me = await api.me();
      setRole(me.role);
      message.success("登录成功");
      navigate("/");
    } catch (e: any) {
      message.error(e.message || "登录失败");
    }
  };

  return (
    <div style={{ display: "flex", height: "100vh", alignItems: "center", justifyContent: "center" }}>
      <Card title="登录" style={{ width: 360 }}>
        <Form form={form} onFinish={onFinish} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>
            登录
          </Button>
        </Form>
      </Card>
    </div>
  );
}
