// MIT. Synthetic detector controls, invoked only by tools/check-memory.py.
#include <climits>
#include <memory>
#include <string_view>

namespace {
// Runtime inputs and noinline keep the deliberate faults observable in Release.
[[gnu::noinline]] int addressControl(unsigned index) {
  auto bytes = std::make_unique<unsigned char[]>(8);
  volatile unsigned char *pointer = bytes.get();
  return pointer[index];
}

[[gnu::noinline]] int undefinedControl(int value) { return value + 1; }
} // namespace

int main(int argc, char **argv) {
  if (argc == 2 && std::string_view(argv[1]) == "--address-control") {
    return addressControl(8);
  }
  if (argc == 2 && std::string_view(argv[1]) == "--undefined-control") {
    return undefinedControl(INT_MAX);
  }
  return 2;
}
