import time
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

t0 = time.perf_counter()
pwd_context.hash("testpassword")
t1 = time.perf_counter()
print(f"Bcrypt hash took {(t1 - t0) * 1000:.2f}ms")

h = pwd_context.hash("testpassword")
t0 = time.perf_counter()
pwd_context.verify("testpassword", h)
t1 = time.perf_counter()
print(f"Bcrypt verify took {(t1 - t0) * 1000:.2f}ms")
