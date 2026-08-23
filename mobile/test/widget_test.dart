import 'package:flutter_test/flutter_test.dart';
import 'package:nexus_mind_mobile/main.dart';

void main() {
  testWidgets('Nexus Mind Enterprise App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const NexusMindEnterpriseApp());
    expect(find.byType(NexusMindEnterpriseApp), findsOneWidget);
  });
}
