import 'package:flutter/material.dart';
import '../theme.dart';
import 'shimmer.dart';

class AnalyzerSkeleton extends StatelessWidget {
  const AnalyzerSkeleton({super.key});
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // header skeleton
        Center(
          child: Column(children: [
            AdvancedShimmer(child: Container(height: 22, width: 140, decoration: BoxDecoration(color: T.borderLight, borderRadius: BorderRadius.circular(100)))),
            const SizedBox(height: 12),
            const SkeletonBlock(height: 28, width: 200, radius: 8),
            const SizedBox(height: 8),
            const SkeletonBlock(height: 14, width: 280, radius: 6),
            const SkeletonBlock(height: 14, width: 220, radius: 6, margin: EdgeInsets.only(top: 6)),
          ]),
        ),
        const SizedBox(height: 18),
        Row(mainAxisAlignment: MainAxisAlignment.center, children: [for (int i = 0; i < 3; i++) Container(margin: const EdgeInsets.symmetric(horizontal: 6), height: 18, width: 72, decoration: BoxDecoration(color: T.borderLight, borderRadius: BorderRadius.circular(100)))]),
        const SizedBox(height: 20),
        Skeleton.card(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Skeleton.line(width: 90, height: 12),
            const SizedBox(height: 8),
            SkeletonBlock(height: 46, width: double.infinity, radius: T.radiusLg),
            const SizedBox(height: 18),
            SkeletonBlock(height: 108, width: double.infinity, radius: T.radiusXl),
            const SizedBox(height: 18),
            SkeletonBlock(height: 46, width: double.infinity, radius: T.radiusLg),
            const SizedBox(height: 10),
            Center(child: Skeleton.line(width: 180, height: 10)),
          ]),
        ),
      ],
    );
  }
}

class ResultSkeleton extends StatelessWidget {
  const ResultSkeleton({super.key});
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Center(child: Skeleton.line(width: 140, height: 18)),
        const SizedBox(height: 10),
        Center(child: SkeletonBlock(height: 22, width: 160, radius: 8)),
        const SizedBox(height: 6),
        Center(child: Skeleton.line(width: 200, height: 11)),
        const SizedBox(height: 16),
        Skeleton.card(
          child: Row(children: [
            Skeleton.circle(96),
            const SizedBox(width: 16),
            Expanded(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Skeleton.line(width: 110, height: 14),
                const SizedBox(height: 8),
                Skeleton.line(width: double.infinity, height: 11),
                Skeleton.line(width: 180, height: 11, margin: const EdgeInsets.only(top: 6)),
                const SizedBox(height: 10),
                Row(children: [SkeletonBlock(height: 20, width: 80, radius: 100), const SizedBox(width: 8), SkeletonBlock(height: 20, width: 100, radius: 100)]),
              ]),
            ),
          ]),
        ),
        const SizedBox(height: 12),
        Skeleton.card(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [Skeleton.circle(28), const SizedBox(width: 10), Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Skeleton.line(width: 110, height: 12), const SizedBox(height: 4), Skeleton.line(width: 160, height: 10)])]),
            const SizedBox(height: 14),
            Wrap(spacing: 8, runSpacing: 8, children: [for (int i = 0; i < 6; i++) SkeletonBlock(height: 22, width: 72 + (i % 2) * 18, radius: 100)]),
          ]),
        ),
        const SizedBox(height: 12),
        Skeleton.card(
          child: Column(
            children: [
              Row(children: [Skeleton.circle(28), const SizedBox(width: 10), Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Skeleton.line(width: 110, height: 12), const SizedBox(height: 4), Skeleton.line(width: 140, height: 10)])]),
              const SizedBox(height: 14),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(children: [for (int i = 0; i < 4; i++) Container(margin: const EdgeInsets.only(right: 10), width: 132, height: 110, decoration: BoxDecoration(color: T.borderLight, borderRadius: BorderRadius.circular(T.radiusLg)))]),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        Skeleton.card(
          child: Column(children: [for (int i = 0; i < 3; i++) Container(margin: EdgeInsets.only(bottom: i == 2 ? 0 : 8), height: 56, decoration: BoxDecoration(color: T.borderLight, borderRadius: BorderRadius.circular(T.radiusLg)))]),
        ),
      ],
    );
  }
}

class ProfileSkeleton extends StatelessWidget {
  const ProfileSkeleton({super.key});
  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Skeleton.card(
        child: Row(children: [
          Skeleton.circle(56),
          const SizedBox(width: 14),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Skeleton.line(width: 120, height: 14), const SizedBox(height: 6), Skeleton.line(width: 180, height: 11), const SizedBox(height: 8), Row(children: [SkeletonBlock(height: 18, width: 56, radius: 100), const SizedBox(width: 6), SkeletonBlock(height: 18, width: 70, radius: 100)])])),
        ]),
      ),
      const SizedBox(height: 14),
      Skeleton.card(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [Skeleton.circle(28), const SizedBox(width: 10), Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Skeleton.line(width: 110, height: 12), const SizedBox(height: 4), Skeleton.line(width: 80, height: 10)])]),
          const SizedBox(height: 12),
          SkeletonBlock(height: 36, width: double.infinity, radius: 10),
          const SizedBox(height: 10),
          for (int i = 0; i < 3; i++) Container(margin: const EdgeInsets.only(bottom: 8), child: Row(children: [Skeleton.circle(36), const SizedBox(width: 10), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Skeleton.line(width: double.infinity, height: 12), const SizedBox(height: 6), Skeleton.line(width: 140, height: 10)])) , SkeletonBlock(height: 22, width: 44, radius: 100)])),
        ]),
      ),
    ]);
  }
}

class InterviewSkeleton extends StatelessWidget {
  const InterviewSkeleton({super.key});
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SkeletonBlock(height: 64, width: 64, radius: 18),
        const SizedBox(height: 12),
        Skeleton.line(width: 140, height: 12),
        const SizedBox(height: 8),
        SkeletonBlock(height: 22, width: 180, radius: 8),
        const SizedBox(height: 6),
        SkeletonBlock(height: 12, width: 220, radius: 6),
        const SizedBox(height: 18),
        Skeleton.card(
          child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            Skeleton.line(width: 90, height: 11),
            const SizedBox(height: 8),
            SkeletonBlock(height: 46, width: double.infinity, radius: T.radiusLg),
            const SizedBox(height: 14),
            SkeletonBlock(height: 46, width: double.infinity, radius: T.radiusLg),
          ]),
        ),
      ],
    );
  }
}

class CoverLetterSkeleton extends StatelessWidget {
  const CoverLetterSkeleton({super.key});
  @override
  Widget build(BuildContext context) {
    return Column(children: [
      SkeletonBlock(height: 64, width: 64, radius: 18),
      const SizedBox(height: 12),
      Skeleton.line(width: 140, height: 12),
      const SizedBox(height: 8),
      SkeletonBlock(height: 22, width: 180, radius: 8),
      const SizedBox(height: 18),
      Skeleton.card(
        child: Column(children: [
          for (int i = 0; i < 4; i++) ...[
            Skeleton.line(width: 90, height: 11),
            const SizedBox(height: 6),
            SkeletonBlock(height: 46, width: double.infinity, radius: T.radiusLg),
            const SizedBox(height: 12),
          ],
          SkeletonBlock(height: 46, width: double.infinity, radius: T.radiusLg),
        ]),
      ),
    ]);
  }
}

class ChatSkeleton extends StatelessWidget {
  const ChatSkeleton({super.key});
  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: 4,
      separatorBuilder: (_, __) => const SizedBox(height: 10),
      itemBuilder: (_, i) {
        final isUser = i.isOdd;
        return Align(
          alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
          child: Container(
            width: 220 + (i % 2) * 30,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: T.borderLight, borderRadius: BorderRadius.circular(14)),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Skeleton.line(width: double.infinity, height: 10), const SizedBox(height: 6), Skeleton.line(width: 160, height: 10), if (i == 0) ...[const SizedBox(height: 6), Skeleton.line(width: 120, height: 10)]]),
          ),
        );
      },
    );
  }
}
